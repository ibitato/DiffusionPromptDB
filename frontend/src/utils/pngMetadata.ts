import { inflate } from 'pako';

export interface StableDiffusionMetadata {
  positivePrompt: string;
  negativePrompt?: string;
  settings: Record<string, string>;
  rawParameters: string;
}

const PNG_SIGNATURE = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);

export async function parseStableDiffusionMetadata(file: File): Promise<StableDiffusionMetadata> {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);

  if (!matchesSignature(bytes)) {
    throw new Error('Selected file is not a valid PNG.');
  }

  const parametersText = extractParametersChunk(bytes);
  if (!parametersText) {
    throw new Error('PNG does not contain Stable Diffusion metadata.');
  }

  return splitParametersBlob(parametersText);
}

function matchesSignature(bytes: Uint8Array): boolean {
  return PNG_SIGNATURE.every((byte, index) => bytes[index] === byte);
}

function extractParametersChunk(bytes: Uint8Array): string | null {
  let offset = 8; // Skip signature

  while (offset < bytes.length) {
    const length = readUint32(bytes, offset);
    const type = readChunkType(bytes, offset + 4);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    const chunkData = bytes.subarray(dataStart, dataEnd);

    if (type === 'tEXt') {
      const text = decodeTextChunk(chunkData);
      if (text) return text;
    } else if (type === 'iTXt') {
      const text = decodeInternationalTextChunk(chunkData);
      if (text) return text;
    } else if (type === 'zTXt') {
      const text = decodeCompressedTextChunk(chunkData);
      if (text) return text;
    }

    offset = dataEnd + 4; // Skip CRC

    if (type === 'IEND') break;
  }

  return null;
}

function readUint32(bytes: Uint8Array, offset: number): number {
  return (
    (bytes[offset] << 24) |
    (bytes[offset + 1] << 16) |
    (bytes[offset + 2] << 8) |
    bytes[offset + 3]
  );
}

function readChunkType(bytes: Uint8Array, offset: number): string {
  return String.fromCharCode(bytes[offset], bytes[offset + 1], bytes[offset + 2], bytes[offset + 3]);
}

function decodeTextChunk(chunkData: Uint8Array): string | null {
  const nullIndex = chunkData.indexOf(0);
  if (nullIndex === -1) return null;
  const keyword = new TextDecoder('latin1').decode(chunkData.slice(0, nullIndex));
  if (keyword !== 'parameters') return null;
  return new TextDecoder().decode(chunkData.slice(nullIndex + 1));
}

function decodeCompressedTextChunk(chunkData: Uint8Array): string | null {
  const nullIndex = chunkData.indexOf(0);
  if (nullIndex === -1 || nullIndex + 2 >= chunkData.length) return null;
  const keyword = new TextDecoder('latin1').decode(chunkData.slice(0, nullIndex));
  if (keyword !== 'parameters') return null;
  const compression = chunkData[nullIndex + 1];
  if (compression !== 0) return null;
  const compressed = chunkData.slice(nullIndex + 2);
  const text = inflate(compressed, { to: 'string' });
  return text;
}

function decodeInternationalTextChunk(chunkData: Uint8Array): string | null {
  let cursor = 0;

  const keywordEnd = chunkData.indexOf(0, cursor);
  if (keywordEnd === -1) return null;
  const keyword = new TextDecoder('latin1').decode(chunkData.slice(cursor, keywordEnd));
  if (keyword !== 'parameters') return null;
  cursor = keywordEnd + 1;

  const compressionFlag = chunkData[cursor];
  cursor += 1;
  const compressionMethod = chunkData[cursor];
  cursor += 1;
  if (compressionMethod !== 0) return null;

  // language tag
  const languageEnd = chunkData.indexOf(0, cursor);
  if (languageEnd === -1) return null;
  cursor = languageEnd + 1;

  // translated keyword
  const translatedEnd = chunkData.indexOf(0, cursor);
  if (translatedEnd === -1) return null;
  cursor = translatedEnd + 1;

  const textData = chunkData.slice(cursor);
  if (compressionFlag === 1) {
    return inflate(textData, { to: 'string' });
  }
  return new TextDecoder().decode(textData);
}

function splitParametersBlob(blob: string): StableDiffusionMetadata {
  const lines = blob.split('\n');
  const positiveLines: string[] = [];
  const negativeLines: string[] = [];
  const infoLines: string[] = [];

  let section: 'positive' | 'negative' | 'info' = 'positive';

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (section === 'positive') {
      if (line.startsWith('Negative prompt:')) {
        section = 'negative';
        negativeLines.push(line.replace('Negative prompt:', '').trim());
      } else if (isInfoLine(line)) {
        section = 'info';
        infoLines.push(line);
      } else {
        positiveLines.push(line);
      }
    } else if (section === 'negative') {
      if (isInfoLine(line)) {
        section = 'info';
        infoLines.push(line);
      } else {
        negativeLines.push(line.replace('Negative prompt:', '').trim());
      }
    } else {
      infoLines.push(line);
    }
  }

  return {
    positivePrompt: positiveLines.join('\n').trim(),
    negativePrompt: negativeLines.join('\n').trim() || undefined,
    settings: parseSettings(infoLines),
    rawParameters: blob,
  };
}

function isInfoLine(line: string): boolean {
  return /^[A-Za-z0-9 _/+().-]+: /.test(line);
}

function parseSettings(lines: string[]): Record<string, string> {
  const merged = lines.join(' ');
  const parts = merged.split(/,\s*/);
  const result: Record<string, string> = {};
  let currentKey: string | null = null;

  for (const part of parts) {
    if (!part) continue;
    if (part.includes(':')) {
      const [key, value] = part.split(':', 2);
      currentKey = key.trim();
      result[currentKey] = value.trim();
    } else if (currentKey) {
      result[currentKey] = `${result[currentKey]}, ${part.trim()}`;
    }
  }

  return result;
}

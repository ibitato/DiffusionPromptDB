import { StableDiffusionMetadata } from './pngMetadata';

const STOPWORDS = new Set([
  'and',
  'with',
  'the',
  'of',
  'in',
  'at',
  'by',
  'for',
  'to',
  'a',
  'an',
  'on',
]);

const UNSAFE_PROMPT_CHARS = ['(', ')', '[', ']', '{', '}', '<', '>', ':', '"', "'", '|', '*'];
const ART_STYLE_KEYWORDS: Array<[string, string]> = [
  ['anime', 'Anime'],
  ['manga', 'Anime'],
  ['comic', 'Comic Book'],
  ['watercolor', 'Watercolor'],
  ['oil painting', 'Oil Painting'],
  ['digital painting', 'Digital Painting'],
  ['cinematic', 'Cinematic'],
  ['film still', 'Cinematic'],
  ['photograph', 'Photorealistic'],
  ['photo', 'Photorealistic'],
  ['realistic', 'Realistic'],
  ['hyperrealistic', 'Photorealistic'],
  ['fantasy', 'Fantasy Art'],
  ['cyberpunk', 'Cyberpunk'],
  ['pixel', 'Pixel Art'],
  ['low poly', 'Low Poly'],
  ['3d render', '3D Render'],
  ['render', '3D Render'],
];

export function inferTagsFromPrompt(prompt: string | undefined, limit = 20): string[] {
  if (!prompt) return [];
  const sanitizeChunk = (chunk: string) =>
    UNSAFE_PROMPT_CHARS.reduce((acc, char) => acc.split(char).join(' '), chunk);

  const tokens = prompt
    .split(/[,\n]+/)
    .map((chunk) =>
      sanitizeChunk(chunk)
        .trim()
        .toLowerCase(),
    )
    .flatMap((chunk) => chunk.split(/\\s+/))
    .map((token) => token.trim().replace(/^-+|-+$/g, ''))
    .filter((token) => token.length > 1 && !STOPWORDS.has(token));

  const seen = new Set<string>();
  const result: string[] = [];

  for (const token of tokens) {
    if (!seen.has(token)) {
      seen.add(token);
      result.push(token);
    }
    if (result.length >= limit) break;
  }

  return result;
}

export function inferArtStyleFromMetadata(metadata: StableDiffusionMetadata): string | '' {
  const corpus = (
    (metadata.positivePrompt || '') +
    ' ' +
    (metadata.rawParameters || '') +
    ' ' +
    ((metadata.settings.Model as string) || metadata.settings.model || '')
  ).toLowerCase();

  for (const [keyword, style] of ART_STYLE_KEYWORDS) {
    if (corpus.includes(keyword)) {
      return style;
    }
  }

  return '';
}

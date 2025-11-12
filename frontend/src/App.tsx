import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">DiffusionPromptDB</h1>
        <p className="text-xl mb-8">Sistema de Catalogación de Prompts</p>
        
        <div className="space-y-4">
          <div className="bg-slate-800 p-6 rounded-lg">
            <h2 className="text-2xl mb-2">Frontend Funcionando ✅</h2>
            <p className="text-gray-400">React + TypeScript + Tailwind CSS</p>
          </div>
          
          <div className="bg-blue-600 p-4 rounded-lg">
            <p>Usuario disponible: <strong>test / test</strong></p>
            <p className="text-sm">Backend API: http://localhost:8000</p>
          </div>
          
          <button
            onClick={() => setCount(count + 1)}
            className="bg-violet-600 hover:bg-violet-700 px-6 py-3 rounded-lg font-medium"
          >
            Contador: {count}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

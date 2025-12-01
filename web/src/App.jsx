import { useState } from 'react'
import { Coins, Loader2, AlertCircle, Camera, RefreshCw } from 'lucide-react'
import CameraCapture from './components/CameraCapture'
import PreprocessingSteps from './components/PreprocessingSteps'
import PredictionResult from './components/PredictionResult'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [result, setResult] = useState(null) // API response
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCapture = async (imageBlob) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', imageBlob, 'capture.jpg')

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 py-4 px-6 shadow-lg border-b border-gray-700">
        <div className="flex items-center justify-center gap-3">
          <Coins className="w-8 h-8 text-yellow-500" />
          <h1 className="text-2xl font-bold">Klasifikasi Koin Rupiah</h1>
        </div>
        <p className="text-gray-400 text-center text-sm mt-1">
          Edge Detection + CNN
        </p>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl flex-1 flex flex-col justify-center">
        {/* Step 1: Camera/Upload */}
        {!result && !loading && (
          <CameraCapture onCapture={handleCapture} loading={loading} />
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto" />
            <p className="mt-4 text-gray-400">Memproses gambar...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
            <button
              onClick={handleReset}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Coba Lagi
            </button>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-8">
            {/* Preprocessing Steps */}
            <PreprocessingSteps steps={result.preprocessing_steps} />

            {/* Prediction Results */}
            <PredictionResult
              predictions={result.predictions}
              circleDetected={result.circle_detected}
            />

            {/* Reset Button */}
            <div className="text-center">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold inline-flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                Ambil Foto Baru
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 py-4 text-center text-gray-500 text-sm border-t border-gray-700 mt-auto">
        Pengolahan Citra - Semester 5
      </footer>
    </div>
  )
}

export default App

import {
  Brain,
  TreeDeciduous,
  AlertTriangle,
  CheckCircle2,
  Zap,
  BarChart3,
  Layers,
  Clock,
  Target,
  Hash
} from 'lucide-react'

// Format class name nicely
const formatClassName = (className) => {
  if (!className) return 'Unknown'
  // e.g., "Koin Rp 1000 - angka" -> "Rp 1.000 (Angka)"
  // Handle both formats: "Koin Rp 1000 - angka" and "Koin Rp 1000_angka"
  const parts = className.includes(' - ') ? className.split(' - ') : className.split('_')
  const nominal = parts[0]?.replace('Koin Rp ', 'Rp ') || ''
  const side = parts[1] || ''

  // Format number with dots (Indonesian style)
  const formattedNominal = nominal.replace(/(\d+)/, (match) => {
    return parseInt(match).toLocaleString('id-ID')
  })

  const sideLabel = side === 'angka' ? '(Angka)' : side === 'gambar' ? '(Gambar)' : ''
  return `${formattedNominal} ${sideLabel}`.trim()
}

// Get confidence color
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.9) return 'bg-green-500'
  if (confidence >= 0.7) return 'bg-yellow-500'
  if (confidence >= 0.5) return 'bg-orange-500'
  return 'bg-red-500'
}

// Render single model result
function ModelResult({ title, icon: Icon, data, isPrimary, modelInfo }) {
  if (!data) return null
  if (data.error) return (
    <div className="rounded-xl p-6 bg-gray-800">
      <h3 className="text-lg font-bold flex items-center gap-2"><Icon className="w-5 h-5" /> {title}</h3>
      <p className="text-red-400 mt-4">Error: {data.error}</p>
    </div>
  )

  const confidence = data.confidence || 0
  const confidencePercent = (confidence * 100).toFixed(2)
  // Use 'label' from API response
  const predictionLabel = data.label || data.prediction || 'Unknown'

  return (
    <div className={`rounded-xl p-6 ${isPrimary ? 'bg-linear-to-br from-blue-900 to-purple-900 border-2 border-blue-500' : 'bg-gray-800 border border-gray-700'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Icon className="w-5 h-5" />
          {title}
        </h3>
        {isPrimary && (
          <span className="bg-blue-600 text-xs px-2 py-1 rounded font-semibold">PRIMARY</span>
        )}
      </div>

      {/* Model info badge */}
      {modelInfo && (
        <div className="flex flex-wrap gap-2 mb-3">
          <span className="text-xs bg-gray-700/80 px-2 py-1 rounded inline-flex items-center gap-1">
            <BarChart3 className="w-3 h-3" />
            Akurasi: {modelInfo.accuracy}
          </span>
          <span className="text-xs bg-gray-700/80 px-2 py-1 rounded inline-flex items-center gap-1">
            <Layers className="w-3 h-3" />
            {modelInfo.type}
          </span>
        </div>
      )}

      {/* Prediction */}
      <div className="text-center py-4">
        <p className="text-3xl font-bold text-white mb-2">
          {formatClassName(predictionLabel)}
        </p>

        {/* Confidence bar */}
        <div className="w-full bg-gray-700 rounded-full h-4 mt-4">
          <div
            className={`h-4 rounded-full transition-all duration-500 ${getConfidenceColor(confidence)}`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
        <p className="text-sm text-gray-400 mt-2">
          Confidence: <span className="font-bold text-white">{confidencePercent}%</span>
        </p>
      </div>

      {/* Processing time */}
      {data.processing_time_ms && (
        <div className="text-center mb-4">
          <span className="text-xs text-gray-500 inline-flex items-center gap-1">
            <Zap className="w-3 h-3" />
            Waktu inferensi: <span className="text-gray-300">{data.processing_time_ms} ms</span>
          </span>
        </div>
      )}

      {/* Top probabilities - API returns all_classes array */}
      {data.all_classes && (
        <div className="mt-4">
          <p className="text-sm text-gray-400 mb-2">Distribusi Probabilitas:</p>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {[...data.all_classes]
              .sort((a, b) => b.confidence - a.confidence)
              .slice(0, 5)
              .map((item) => (
                <div key={item.label} className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 w-28 truncate">
                    {formatClassName(item.label)}
                  </span>
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getConfidenceColor(item.confidence)}`}
                      style={{ width: `${item.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400 w-12 text-right">
                    {(item.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Model metadata
const MODEL_INFO = {
  cnn: {
    accuracy: '~95%',
    type: 'CNN 256x256',
  },
  random_forest: {
    accuracy: '~75%',
    type: '35 Edge Features',
  }
}

function PredictionResult({ predictions, circleDetected }) {
  if (!predictions) return null

  const { cnn, random_forest } = predictions

  return (
    <div className="space-y-6">
      {/* Circle Detection Warning */}
      {!circleDetected && (
        <div className="bg-yellow-900/50 border border-yellow-500 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-yellow-400 shrink-0" />
          <div>
            <p className="font-semibold text-yellow-400">Koin tidak terdeteksi dengan baik</p>
            <p className="text-sm text-yellow-300/70">
              Hough Circle Transform tidak menemukan lingkaran. Hasil mungkin kurang akurat.
            </p>
          </div>
        </div>
      )}

      {/* Results Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <ModelResult
          title="CNN Model"
          icon={Brain}
          data={cnn}
          isPrimary={true}
          modelInfo={MODEL_INFO.cnn}
        />
        <ModelResult
          title="Random Forest"
          icon={TreeDeciduous}
          data={random_forest}
          isPrimary={false}
          modelInfo={MODEL_INFO.random_forest}
        />
      </div>

      {/* Stats Summary */}
      {cnn && random_forest && !cnn.error && !random_forest.error && (
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-gray-500 text-xs flex items-center justify-center gap-1">
                <Clock className="w-3 h-3" /> Total Waktu
              </p>
              <p className="text-white font-semibold">
                {((cnn.processing_time_ms || 0) + (random_forest.processing_time_ms || 0)).toFixed(0)} ms
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-xs flex items-center justify-center gap-1">
                <Target className="w-3 h-3" /> CNN Confidence
              </p>
              <p className="text-green-400 font-semibold">{(cnn.confidence * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs flex items-center justify-center gap-1">
                <Target className="w-3 h-3" /> RF Confidence
              </p>
              <p className={`font-semibold ${random_forest.confidence >= 0.5 ? 'text-yellow-400' : 'text-red-400'}`}>
                {(random_forest.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-xs flex items-center justify-center gap-1">
                <Hash className="w-3 h-3" /> Jumlah Kelas
              </p>
              <p className="text-white font-semibold">8 kelas</p>
            </div>
          </div>
        </div>
      )}

      {/* Comparison */}
      {cnn && random_forest && !cnn.error && !random_forest.error && (
        <div className="bg-gray-800 rounded-xl p-4 text-center border border-gray-700">
          {cnn.label === random_forest.label ? (
            <p className="text-green-400 flex items-center justify-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              Kedua model memprediksi hasil yang sama
            </p>
          ) : (
            <p className="text-yellow-400 flex items-center justify-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Model memberikan prediksi berbeda - gunakan hasil CNN sebagai acuan utama
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default PredictionResult

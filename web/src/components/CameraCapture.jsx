import { useState, useRef, useCallback, useEffect } from 'react'
import {
  Upload,
  Camera,
  Video,
  VideoOff,
  AlertCircle,
  Globe,
  RefreshCw,
  Loader2,
  Lightbulb,
  CircleDot,
  Sun,
  Focus,
  EyeOff,
  Fullscreen
} from 'lucide-react'

function CameraCapture({ onCapture, loading }) {
  const [mode, setMode] = useState('upload') // 'upload' or 'camera'
  const [cameraActive, setCameraActive] = useState(false)
  const [cameraState, setCameraState] = useState('idle') // 'idle' | 'requesting' | 'denied' | 'not-supported' | 'active'
  const [stream, setStream] = useState(null)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const fileInputRef = useRef(null)

  // Start camera with proper permission handling
  const startCamera = useCallback(async () => {
    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraState('not-supported')
      return
    }

    setCameraState('requesting')

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 640, height: 480 }
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setCameraActive(true)
      setCameraState('active')
    } catch (err) {
      console.error('Camera error:', err)
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setCameraState('denied')
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setCameraState('not-found')
      } else {
        setCameraState('error')
      }
    }
  }, [])

  // Stop camera
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setCameraActive(false)
    setCameraState('idle')
  }, [stream])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  // Capture photo from camera
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)

    canvas.toBlob((blob) => {
      if (blob) {
        stopCamera()
        onCapture(blob)
      }
    }, 'image/jpeg', 0.95)
  }

  // Handle file upload
  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      onCapture(file)
    }
  }

  // Handle drag and drop
  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith('image/')) {
      onCapture(file)
    }
  }

  return (
    <div className="space-y-6">
      {/* Tab Selector */}
      <div className="max-w-md mx-auto">
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => { setMode('upload'); stopCamera() }}
            className={`flex-1 py-3 px-4 font-medium transition-all inline-flex items-center justify-center gap-2 border-b-2 -mb-px rounded-t-lg ${mode === 'upload'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500 hover:bg-gray-700/50'
              }`}
          >
            <Upload className="w-4 h-4" />
            Upload Gambar
          </button>
          <button
            onClick={() => { setMode('camera'); startCamera() }}
            className={`flex-1 py-3 px-4 font-medium transition-all inline-flex items-center justify-center gap-2 border-b-2 -mb-px rounded-t-lg ${mode === 'camera'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500 hover:bg-gray-700/50'
              }`}
          >
            <Camera className="w-4 h-4" />
            Kamera
          </button>
        </div>
      </div>

      {/* Upload Mode */}
      {mode === 'upload' && (
        <div
          className="border-2 border-dashed border-gray-600 rounded-xl p-12 text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800/50 transition"
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <CircleDot className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <p className="text-lg text-gray-300 mb-2">
            Klik atau drag & drop gambar koin
          </p>
          <p className="text-sm text-gray-500">
            Format: JPG, PNG, JPEG
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      )}

      {/* Camera Mode */}
      {mode === 'camera' && (
        <div className="relative max-w-lg mx-auto">
          {/* Video Feed */}
          <div className="relative rounded-xl overflow-hidden bg-black aspect-4/3">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />

            {/* Circle Overlay Guide */}
            {cameraActive && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-64 h-64 border-4 border-green-400 rounded-full opacity-70">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="bg-black/50 px-3 py-1 rounded text-sm text-green-400">
                      Posisikan koin di sini
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Camera state overlays */}
            {mode === 'camera' && !cameraActive && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                {/* Requesting permission */}
                {cameraState === 'requesting' && (
                  <div className="text-center p-6">
                    <Video className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
                    <p className="text-white font-semibold">Meminta izin kamera...</p>
                    <p className="text-gray-400 text-sm mt-2">Klik "Izinkan" pada popup browser</p>
                  </div>
                )}

                {/* Permission denied */}
                {cameraState === 'denied' && (
                  <div className="text-center p-6">
                    <VideoOff className="w-12 h-12 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400 font-semibold">Akses Kamera Ditolak</p>
                    <p className="text-gray-400 text-sm mt-2 max-w-xs">
                      Browser memblokir akses kamera. Untuk mengaktifkan:
                    </p>
                    <ol className="text-gray-400 text-sm mt-2 text-left max-w-xs mx-auto list-decimal list-inside">
                      <li>Klik ikon gembok di address bar</li>
                      <li>Cari "Camera" atau "Kamera"</li>
                      <li>Ubah ke "Allow" atau "Izinkan"</li>
                      <li>Refresh halaman ini</li>
                    </ol>
                    <button
                      onClick={() => { setCameraState('idle'); startCamera() }}
                      className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm inline-flex items-center gap-2"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Coba Lagi
                    </button>
                  </div>
                )}

                {/* Camera not found */}
                {cameraState === 'not-found' && (
                  <div className="text-center p-6">
                    <VideoOff className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                    <p className="text-yellow-400 font-semibold">Kamera Tidak Ditemukan</p>
                    <p className="text-gray-400 text-sm mt-2">
                      Tidak ada kamera yang terdeteksi pada perangkat ini.
                    </p>
                    <button
                      onClick={() => setMode('upload')}
                      className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm inline-flex items-center gap-2"
                    >
                      <Upload className="w-4 h-4" />
                      Upload Gambar
                    </button>
                  </div>
                )}

                {/* Browser not supported */}
                {cameraState === 'not-supported' && (
                  <div className="text-center p-6">
                    <Globe className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                    <p className="text-yellow-400 font-semibold">Browser Tidak Mendukung</p>
                    <p className="text-gray-400 text-sm mt-2">
                      Browser ini tidak mendukung akses kamera.<br />
                      Gunakan Chrome, Firefox, atau Edge terbaru.
                    </p>
                    <button
                      onClick={() => setMode('upload')}
                      className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm inline-flex items-center gap-2"
                    >
                      <Upload className="w-4 h-4" />
                      Upload Gambar
                    </button>
                  </div>
                )}

                {/* Generic error */}
                {cameraState === 'error' && (
                  <div className="text-center p-6">
                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400 font-semibold">Gagal Mengakses Kamera</p>
                    <p className="text-gray-400 text-sm mt-2">
                      Terjadi kesalahan saat mengakses kamera.
                    </p>
                    <button
                      onClick={() => { setCameraState('idle'); startCamera() }}
                      className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm inline-flex items-center gap-2"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Coba Lagi
                    </button>
                  </div>
                )}

                {/* Idle - waiting to start */}
                {cameraState === 'idle' && (
                  <div className="text-center p-6">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
                    <p className="text-gray-400">Memulai kamera...</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Capture Button */}
          {cameraActive && (
            <div className="text-center mt-4">
              <button
                onClick={capturePhoto}
                disabled={loading}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-full font-semibold text-lg shadow-lg transition inline-flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                Ambil Foto
              </button>
            </div>
          )}

          {/* Hidden canvas for capture */}
          <canvas ref={canvasRef} className="hidden" />
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-800 rounded-lg p-4 max-w-lg mx-auto">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-yellow-400" />
          Tips untuk hasil terbaik:
        </h3>
        <ul className="text-sm text-gray-400 space-y-2">
          <li className="flex items-center gap-2">
            <Fullscreen className="w-4 h-4 text-green-500" />
            Gunakan latar belakang polos dan kontras
          </li>
          <li className="flex items-center gap-2">
            <Sun className="w-4 h-4 text-yellow-500" />
            Pastikan pencahayaan merata
          </li>
          <li className="flex items-center gap-2">
            <Focus className="w-4 h-4 text-blue-400" />
            Posisikan koin di tengah frame
          </li>
          <li className="flex items-center gap-2">
            <EyeOff className="w-4 h-4 text-gray-500" />
            Hindari bayangan pada koin
          </li>
        </ul>
      </div>
    </div>
  )
}

export default CameraCapture

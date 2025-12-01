import { useState } from 'react'
import {
  Image,
  Maximize2,
  Sun,
  Grid3X3,
  Circle,
  Crop,
  CheckCircle2,
  X,
  ZoomIn,
  ArrowRight,
  Microscope
} from 'lucide-react'

function PreprocessingSteps({ steps }) {
  const [selectedImage, setSelectedImage] = useState(null)

  if (!steps) return null

  const stepList = [
    { key: 'original', label: 'Original', Icon: Image },
    { key: 'resized', label: 'Resized', Icon: Maximize2 },
    { key: 'clahe', label: 'CLAHE', Icon: Sun },
    { key: 'sobel', label: 'Sobel Edge', Icon: Grid3X3 },
    { key: 'hough_circle', label: 'Hough Circle', Icon: Circle },
    { key: 'cropped', label: 'Cropped', Icon: Crop },
    { key: 'edge_final', label: 'Final Edge', Icon: CheckCircle2 },
  ]

  return (
    <div className="bg-gray-800 rounded-xl p-6">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Microscope className="w-5 h-5 text-blue-400" />
        Tahapan Preprocessing
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {stepList.map((step, index) => {
          const imageData = steps[step.key]
          if (!imageData) return null
          const StepIcon = step.Icon

          return (
            <div
              key={step.key}
              className="relative cursor-pointer hover:scale-105 transition-transform group"
              onClick={() => setSelectedImage({ ...step, imageData })}
            >
              {/* Step number */}
              <div className="absolute -top-2 -left-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold z-10">
                {index + 1}
              </div>

              {/* Image */}
              <div className="bg-gray-900 rounded-lg overflow-hidden aspect-square">
                <img
                  src={`data:image/png;base64,${imageData}`}
                  alt={step.label}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Label */}
              <p className="text-center text-sm mt-2 text-gray-300 flex items-center justify-center gap-1">
                <StepIcon className="w-3 h-3" />
                {step.label}
              </p>

              {/* Click hint */}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-xs bg-black/50 px-2 py-1 rounded flex items-center gap-1">
                  <ZoomIn className="w-3 h-3" /> Klik
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Modal for enlarged image */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div
            className="relative max-w-2xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-12 right-0 text-white hover:text-red-400 text-lg font-semibold flex items-center gap-2"
            >
              <X className="w-5 h-5" />
              Tutup
            </button>

            {/* Image */}
            <img
              src={`data:image/png;base64,${selectedImage.imageData}`}
              alt={selectedImage.label}
              className="w-full rounded-lg shadow-2xl"
            />

            {/* Label */}
            <p className="text-center text-xl mt-4 text-white flex items-center justify-center gap-2">
              <selectedImage.Icon className="w-5 h-5" />
              {selectedImage.label}
            </p>

            {/* Navigation hint */}
            <p className="text-center text-sm mt-2 text-gray-400">
              Klik di luar gambar atau tombol Tutup untuk menutup
            </p>
          </div>
        </div>
      )}

      {/* Arrow flow indicator */}
      <div className="hidden lg:flex justify-center items-center mt-4 text-gray-500 text-sm gap-1">
        <span>Input</span>
        <ArrowRight className="w-3 h-3" />
        <span>Resize</span>
        <ArrowRight className="w-3 h-3" />
        <span>CLAHE</span>
        <ArrowRight className="w-3 h-3" />
        <span>Sobel</span>
        <ArrowRight className="w-3 h-3" />
        <span>Hough</span>
        <ArrowRight className="w-3 h-3" />
        <span>Crop</span>
        <ArrowRight className="w-3 h-3" />
        <span>CNN</span>
      </div>
    </div>
  )
}

export default PreprocessingSteps

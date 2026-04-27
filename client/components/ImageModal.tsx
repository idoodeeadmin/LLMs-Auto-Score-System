import { X, ZoomIn, ZoomOut, RotateCw, Download } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";

interface ImageModalProps {
  src: string;
  alt?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ImageModal({ src, alt, isOpen, onClose }: ImageModalProps) {
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);

  // Reset transform when closed or src changes
  useEffect(() => {
    if (!isOpen) {
      setScale(1);
      setRotation(0);
    }
  }, [isOpen]);

  const handleZoomIn = (e: React.MouseEvent) => {
    e.stopPropagation();
    setScale(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = (e: React.MouseEvent) => {
    e.stopPropagation();
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleRotate = (e: React.MouseEvent) => {
    e.stopPropagation();
    setRotation(prev => (prev + 90) % 360);
  };

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement("a");
    link.href = src;
    link.download = `image-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-4 md:p-10"
          onClick={onClose}
        >
          {/* Controls Bar */}
          <div className="absolute top-6 right-6 flex items-center gap-3 z-[110]">
            <div className="flex items-center gap-1 bg-white/10 backdrop-blur-md rounded-full border border-white/20 p-1">
              <button onClick={handleZoomIn} className="p-2 text-white hover:bg-white/10 rounded-full transition-colors" title="ซูมเข้า">
                <ZoomIn size={20} />
              </button>
              <button onClick={handleZoomOut} className="p-2 text-white hover:bg-white/10 rounded-full transition-colors" title="ซูมออก">
                <ZoomOut size={20} />
              </button>
              <button onClick={handleRotate} className="p-2 text-white hover:bg-white/10 rounded-full transition-colors" title="หมุนรูป">
                <RotateCw size={20} />
              </button>
              <button onClick={handleDownload} className="p-2 text-white hover:bg-white/10 rounded-full transition-colors" title="ดาวน์โหลด">
                <Download size={20} />
              </button>
            </div>
            <button
              onClick={onClose}
              className="p-2.5 bg-white/10 backdrop-blur-md hover:bg-red-500/80 text-white rounded-full border border-white/20 transition-all"
            >
              <X size={24} />
            </button>
          </div>

          {/* Image Container */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="relative max-w-full max-h-full flex items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <motion.img
              src={src}
              alt={alt || "Expanded view"}
              style={{ 
                scale: scale,
                rotate: rotation
              }}
              className="max-w-full max-h-[85vh] object-contain shadow-2xl rounded-sm transition-transform duration-200 cursor-grab active:cursor-grabbing"
              drag
              dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
            />
          </motion.div>

          {/* Label */}
          {alt && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
              <p className="text-white text-sm font-medium">{alt}</p>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

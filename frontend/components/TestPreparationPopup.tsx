'use client';

import { CheckCircleIcon, HomeIcon, MicrophoneIcon, PencilIcon, SpeakerWaveIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { AnimatePresence, motion } from 'framer-motion';
import { useState, useEffect } from 'react';


interface TestPreparationPopupProps {
  isOpen: boolean
  onClose: () => void
  onStartTest: () => void
}

interface PreparationItem {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  required: boolean
}

const preparationItems: PreparationItem[] = [
  {
    id: "materials",
    title: "Pen and Paper",
    description: "Have writing materials ready for Part 2 preparation",
    icon: PencilIcon,
    required: false,
  },
  {
    id: "environment",
    title: "Quiet Environment",
    description: "Find a quiet room with minimal background noise",
    icon: HomeIcon,
    required: true,
  },
  {
    id: "microphone",
    title: "Microphone Test",
    description: "Ensure your microphone is working and properly connected",
    icon: MicrophoneIcon,
    required: true,
  },
  {
    id: "speakers",
    title: "Speaker/Headphones",
    description: "Test your speakers or headphones for clear audio",
    icon: SpeakerWaveIcon,
    required: true,
  },
];

export function TestPreparationPopup({
  isOpen,
  onClose,
  onStartTest,
}: TestPreparationPopupProps) {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set())

  // Reset checkboxes when popup is closed
  useEffect(() => {
    if (!isOpen) {
      setCheckedItems(new Set())
    }
  }, [isOpen])

  const handleCheckboxChange = (itemId: string) => {
    const newCheckedItems = new Set(checkedItems)
    if (newCheckedItems.has(itemId)) {
      newCheckedItems.delete(itemId)
    } else {
      newCheckedItems.add(itemId)
    }
    setCheckedItems(newCheckedItems)
  }

  const requiredItems = preparationItems.filter(item => item.required)
  const checkedRequiredItems = requiredItems.filter(item => checkedItems.has(item.id))
  const allRequiredChecked = checkedRequiredItems.length === requiredItems.length

  const handleStartTest = () => {
    if (allRequiredChecked) {
      onStartTest()
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-2xl p-6 max-w-md w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-1">
                  Test Preparation
                </h2>
                <p className="text-gray-400 text-sm">
                  Ensure optimal conditions for your IELTS test
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors p-1"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Checklist */}
            <div className="space-y-4 mb-6">
              {preparationItems.map((item) => {
                const Icon = item.icon
                const isChecked = checkedItems.has(item.id)
                const isRequired = item.required

                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * preparationItems.indexOf(item) }}
                    className={`flex items-start space-x-3 p-3 rounded-lg border transition-all duration-200 ${
                      isChecked
                        ? 'border-green-500/50 bg-green-500/10'
                        : 'border-white/10 bg-white/5'
                    }`}
                  >
                    <button
                      onClick={() => handleCheckboxChange(item.id)}
                      className={`flex-shrink-0 w-5 h-5 rounded border-2 transition-all duration-200 flex items-center justify-center ${
                        isChecked
                          ? 'border-green-500 bg-green-500'
                          : 'border-gray-400 hover:border-gray-300'
                      }`}
                    >
                      {isChecked && (
                        <CheckCircleIcon className="w-4 h-4 text-white" />
                      )}
                    </button>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <Icon className="w-4 h-4 text-gray-400" />
                        <h3 className="text-white font-medium text-sm">
                          {item.title}
                          {isRequired && (
                            <span className="text-red-400 ml-1">*</span>
                          )}
                        </h3>
                      </div>
                      <p className="text-gray-400 text-xs leading-relaxed">
                        {item.description}
                      </p>
                    </div>
                  </motion.div>
                )
              })}
            </div>

            {/* Progress Indicator */}
            <div className="mb-6">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">
                  Required items completed
                </span>
                <span className="text-white">
                  {checkedRequiredItems.length}/{requiredItems.length}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(checkedRequiredItems.length / requiredItems.length) * 100}%` }}
                  className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full transition-all duration-300"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-3 text-gray-400 hover:text-white border border-gray-600 hover:border-gray-500 rounded-lg transition-all duration-200 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleStartTest}
                disabled={!allRequiredChecked}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                  allRequiredChecked
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white shadow-lg hover:shadow-amber-500/25'
                    : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                }`}
              >
                Start Test
              </button>
            </div>

            {/* Help Text */}
            {!allRequiredChecked && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-xs text-gray-500 mt-3 text-center"
              >
                Please complete all required items to start the test
              </motion.p>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
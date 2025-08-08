'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { 
  MicrophoneIcon, 
  UserIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface ConnectionLoaderProps {
  isVisible: boolean
  connectionStatus?: 'connecting' | 'connected' | 'failed'
  currentStep?: string
}

interface ConnectionStep {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  duration: number
}

const connectionSteps: ConnectionStep[] = [
  {
    id: 'getting-details',
    title: 'Getting Connection Details',
    description: 'Retrieving secure connection information',
    icon: UserIcon,
    duration: 0, // Will be determined by actual API call
  },
  {
    id: 'connecting',
    title: 'Connecting to Room',
    description: 'Establishing secure WebRTC connection',
    icon: UserIcon,
    duration: 0, // Will be determined by actual connection time
  },
  {
    id: 'enabling-microphone',
    title: 'Enabling Microphone',
    description: 'Activating audio input for the test',
    icon: MicrophoneIcon,
    duration: 0, // Will be determined by actual microphone setup
  },
]

export function ConnectionLoader({ 
  isVisible, 
  connectionStatus = 'connecting',
  currentStep 
}: ConnectionLoaderProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ duration: 0.4, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-2xl p-8 max-w-md w-full"
          >
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4"
              >
                <UserIcon className="w-8 h-8 text-white" />
              </motion.div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Connecting to Examiner
              </h2>
              <p className="text-gray-400 text-sm">
                Please wait while we prepare your IELTS test session
              </p>
            </div>

            {/* Connection Steps */}
            <div className="space-y-4 mb-8">
              {connectionSteps.map((step, index) => (
                <ConnectionStepItem
                  key={step.id}
                  step={step}
                  index={index}
                  isActive={currentStep === step.id}
                  isCompleted={connectionStatus === 'connected' && index < connectionSteps.length - 1}
                />
              ))}
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-400">Connection Progress</span>
                <span className="text-white">
                  {connectionStatus === 'connected' ? 'Connected!' : 
                   connectionStatus === 'failed' ? 'Connection Failed' : 
                   'Establishing...'}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ 
                    width: connectionStatus === 'connected' ? "100%" : 
                           connectionStatus === 'failed' ? "0%" : "50%" 
                  }}
                  transition={{ 
                    duration: 0.5, 
                    ease: "easeInOut"
                  }}
                  className={`h-2 rounded-full ${
                    connectionStatus === 'connected' 
                      ? 'bg-gradient-to-r from-green-500 to-green-400'
                      : connectionStatus === 'failed'
                      ? 'bg-red-500'
                      : 'bg-gradient-to-r from-amber-500 to-orange-500'
                  }`}
                />
              </div>
            </div>

            {/* Loading Animation */}
            <div className="flex justify-center">
              {connectionStatus === 'connecting' && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ 
                    duration: 2, 
                    repeat: Infinity, 
                    ease: "linear" 
                  }}
                  className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full"
                />
              )}
              {connectionStatus === 'connected' && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-6 h-6 text-green-500"
                >
                  <CheckCircleIcon className="w-6 h-6" />
                </motion.div>
              )}
              {connectionStatus === 'failed' && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-6 h-6 text-red-500"
                >
                  <XMarkIcon className="w-6 h-6" />
                </motion.div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

interface ConnectionStepItemProps {
  step: ConnectionStep
  index: number
  isActive: boolean
  isCompleted: boolean
}

function ConnectionStepItem({ 
  step, 
  index, 
  isActive, 
  isCompleted 
}: ConnectionStepItemProps) {
  const Icon = step.icon

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.2 }}
      className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
        isCompleted
          ? 'border-green-500/50 bg-green-500/10'
          : isActive
          ? 'border-amber-500/50 bg-amber-500/10'
          : 'border-white/10 bg-white/5'
      }`}
    >
      <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
        {isCompleted ? (
          <CheckCircleIcon className="w-6 h-6 text-green-500" />
        ) : (
          <motion.div
            animate={isActive ? { scale: [1, 1.1, 1] } : {}}
            transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
          >
            <Icon className={`w-6 h-6 ${
              isActive ? 'text-amber-500' : 'text-gray-400'
            }`} />
          </motion.div>
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <h3 className={`text-sm font-medium ${
          isCompleted ? 'text-green-400' : isActive ? 'text-amber-400' : 'text-white'
        }`}>
          {step.title}
        </h3>
        <p className="text-gray-400 text-xs leading-relaxed">
          {step.description}
        </p>
      </div>

      {isActive && (
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="w-2 h-2 bg-amber-500 rounded-full"
        />
      )}
    </motion.div>
  )
} 
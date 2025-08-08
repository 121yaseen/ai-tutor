'use client'

import {
  BarVisualizer,
  DisconnectButton,
  RoomAudioRenderer,
  RoomContext,
  VideoTrack,
  VoiceAssistantControlBar,
  useVoiceAssistant,
} from '@livekit/components-react'
import { AnimatePresence, motion } from 'framer-motion'
import { Room, RoomEvent } from 'livekit-client'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { CloseIcon } from '@/components/CloseIcon'
import { NoAgentNotification } from '@/components/NoAgentNotification'
import TranscriptionView from '@/components/TranscriptionView'
import { TestPreparationPopup } from '@/components/TestPreparationPopup'
import ParticleBackground from '@/components/ParticleBackground'
import { ConnectionLoader } from '@/components/ConnectionLoader'
import type { ConnectionDetails } from '@/app/api/connection-details/route'

export function VoiceAssistant() {
  const [room] = useState(new Room())
  const [showPreparationPopup, setShowPreparationPopup] = useState(false)
  const [showConnectionLoader, setShowConnectionLoader] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'failed'>('connecting')
  const [currentStep, setCurrentStep] = useState<string>('getting-details')
  const [isTestRunning, setIsTestRunning] = useState(false)
  const [startTimeMs, setStartTimeMs] = useState<number | null>(null)
  const [elapsedMs, setElapsedMs] = useState(0)

  const onConnectButtonClicked = useCallback(async () => {
    setShowPreparationPopup(true)
  }, [])

  const handleStartTest = useCallback(async () => {
    setShowPreparationPopup(false)
    setShowConnectionLoader(true)
    setConnectionStatus('connecting')
    setCurrentStep('getting-details')
    setIsTestRunning(false)
    setStartTimeMs(null)
    setElapsedMs(0)
    
    try {
      // Step 1: Get connection details
      setCurrentStep('getting-details')
      const url = new URL(
        process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ??
          '/api/connection-details',
        window.location.origin
      )
      const response = await fetch(url.toString())
      const connectionDetailsData: ConnectionDetails = await response.json()

      // Step 2: Connect to room
      setCurrentStep('connecting')
      await room.connect(
        connectionDetailsData.serverUrl,
        connectionDetailsData.participantToken
      )
      
      // Step 3: Enable microphone
      setCurrentStep('enabling-microphone')
      await room.localParticipant.setMicrophoneEnabled(true)
      
      // Connection successful
      setConnectionStatus('connected')
      // Start timer
      const now = Date.now()
      setIsTestRunning(true)
      setStartTimeMs(now)
      setElapsedMs(0)
      setTimeout(() => {
        setShowConnectionLoader(false)
      }, 1000) // Show success state for 1 second
    } catch (error) {
      console.error('Connection failed:', error)
      setConnectionStatus('failed')
      setIsTestRunning(false)
      setStartTimeMs(null)
      setTimeout(() => {
        setShowConnectionLoader(false)
      }, 2000) // Show error state for 2 seconds
      // TODO: Show error message to user
    }
  }, [room])

  useEffect(() => {
    room.on(RoomEvent.MediaDevicesError, onDeviceFailure)
    const onDisconnected = () => {
      setIsTestRunning(false)
      setStartTimeMs(null)
    }
    room.on(RoomEvent.Disconnected, onDisconnected)

    return () => {
      room.off(RoomEvent.MediaDevicesError, onDeviceFailure)
      room.off(RoomEvent.Disconnected, onDisconnected)
    }
  }, [room])

  // Tick the timer every second while running
  useEffect(() => {
    if (!isTestRunning || startTimeMs == null) return
    const id = window.setInterval(() => {
      setElapsedMs(Date.now() - startTimeMs)
    }, 1000)
    return () => window.clearInterval(id)
  }, [isTestRunning, startTimeMs])

  const formattedElapsed = useMemo(() => {
    const totalSeconds = Math.floor(elapsedMs / 1000)
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60
    const mm = hours > 0 ? String(minutes).padStart(2, '0') : String(minutes)
    const prefix = hours > 0 ? `${hours}:` : ''
    return `${prefix}${mm}:${String(seconds).padStart(2, '0')}`
  }, [elapsedMs])

  return (
    <RoomContext.Provider value={room}>
      <div className="lk-room-container max-w-[1024px] w-[90vw] mx-auto max-h-[90vh]">
        <SimpleVoiceAssistant onConnectButtonClicked={onConnectButtonClicked} timer={{ running: isTestRunning, text: formattedElapsed }} />
      </div>
      
      <TestPreparationPopup
        isOpen={showPreparationPopup}
        onClose={() => setShowPreparationPopup(false)}
        onStartTest={handleStartTest}
      />
      
      <ConnectionLoader
        isVisible={showConnectionLoader}
        connectionStatus={connectionStatus}
        currentStep={currentStep}
      />
    </RoomContext.Provider>
  )
}

function SimpleVoiceAssistant(props: { onConnectButtonClicked: () => void; timer?: { running: boolean; text: string } }) {
  const { state: agentState } = useVoiceAssistant()

  return (
    <>
      <AnimatePresence mode="wait">
        {agentState === 'disconnected' ? (
          <motion.div
            key="disconnected"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.4, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="relative flex items-center justify-center h-full p-6"
          >
            <ParticleBackground className="opacity-40" maxParticles={80} speed={1} />
            <div className="relative w-full max-w-3xl mx-auto">
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
                <div className="text-center mb-6">
                  <h1 className="text-2xl sm:text-3xl font-light text-white">
                    Ready for your IELTS Speaking practice?
                  </h1>
                  <p className="text-gray-400 mt-2">
                    Talk to the AI Examiner in real-time and get instant scores and feedback.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
                  {[
                    { title: 'Real-time examiner', desc: 'Natural voice conversation' },
                    { title: 'Instant scoring', desc: 'Band score with criteria' },
                    { title: 'Detailed feedback', desc: 'Actionable next steps' },
                  ].map((item) => (
                    <div key={item.title} className="rounded-xl border border-white/10 bg-white/5 p-4">
                      <p className="text-white font-medium text-sm">{item.title}</p>
                      <p className="text-gray-400 text-xs mt-1">{item.desc}</p>
                    </div>
                  ))}
                </div>

                <div className="flex items-center justify-center">
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3, delay: 0.1 }}
                    className="px-6 py-3 rounded-lg text-white font-medium bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 shadow-lg hover:shadow-amber-500/25 transition-colors"
                    onClick={() => props.onConnectButtonClicked()}
                  >
                    Start Test
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="connected"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="flex flex-col items-center gap-4 h-full"
          >
            <AgentVisualizer />
            <div className="flex-1 w-full">
              <TranscriptionView />
            </div>
            <div className="w-full">
              <ControlBar onConnectButtonClicked={props.onConnectButtonClicked} timer={props.timer} />
            </div>
            <RoomAudioRenderer />
            <NoAgentNotification state={agentState} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

function AgentVisualizer() {
  const { state: agentState, videoTrack, audioTrack } = useVoiceAssistant()

  if (videoTrack) {
    return (
      <div className="h-[512px] w-[512px] rounded-lg overflow-hidden">
        <VideoTrack trackRef={videoTrack} />
      </div>
    )
  }
  return (
    <div className="h-[300px] w-full">
      <BarVisualizer
        state={agentState}
        barCount={5}
        trackRef={audioTrack}
        className="agent-visualizer"
        options={{ minHeight: 24 }}
      />
    </div>
  )
}

function ControlBar(props: { onConnectButtonClicked: () => void; timer?: { running: boolean; text: string } }) {
  const { state: agentState } = useVoiceAssistant()

  return (
    <div className="relative h-[60px]">
      <AnimatePresence>
        {agentState === 'disconnected' && (
          <motion.button
            initial={{ opacity: 0, top: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, top: '-10px' }}
            transition={{ duration: 1, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="uppercase absolute left-1/2 -translate-x-1/2 px-4 py-2 bg-white text-black rounded-md hover:bg-gray-100 transition-colors"
            onClick={() => props.onConnectButtonClicked()}
          >
            Start the test
          </motion.button>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {agentState !== 'disconnected' && agentState !== 'connecting' && (
          <motion.div
            initial={{ opacity: 0, top: '10px' }}
            animate={{ opacity: 1, top: 0 }}
            exit={{ opacity: 0, top: '-10px' }}
            transition={{ duration: 0.4, ease: [0.09, 1.04, 0.245, 1.055] }}
            className="flex items-center gap-4 h-8 absolute left-1/2 -translate-x-1/2 justify-center"
          >
            {props.timer && (
              <div className={`px-3 py-1 rounded-md text-sm font-mono border ${props.timer.running ? 'border-amber-400 text-amber-300' : 'border-gray-600 text-gray-300'}`}>
                {props.timer.text}
              </div>
            )}
            <VoiceAssistantControlBar controls={{ leave: false }} />
            <DisconnectButton>
              <CloseIcon />
            </DisconnectButton>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function onDeviceFailure(error: Error) {
  console.error(error)
  alert(
    'Error acquiring camera or microphone permissions. Please make sure you grant the necessary permissions in your browser and reload the tab'
  )
} 
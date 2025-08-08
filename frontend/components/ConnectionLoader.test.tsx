import { render, screen } from '@testing-library/react'
import { ConnectionLoader } from './ConnectionLoader'

// Mock the Heroicons components
jest.mock('@heroicons/react/24/outline', () => ({
  MicrophoneIcon: ({ className }: { className?: string }) => (
    <div data-testid="microphone-icon" className={className} />
  ),
  SpeakerWaveIcon: ({ className }: { className?: string }) => (
    <div data-testid="speaker-wave-icon" className={className} />
  ),
  UserIcon: ({ className }: { className?: string }) => (
    <div data-testid="user-icon" className={className} />
  ),
  CheckCircleIcon: ({ className }: { className?: string }) => (
    <div data-testid="check-circle-icon" className={className} />
  ),
  XMarkIcon: ({ className }: { className?: string }) => (
    <div data-testid="x-mark-icon" className={className} />
  ),
}))

describe('ConnectionLoader', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when isVisible is true', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connecting"
      />
    )

    expect(screen.getByText('Connecting to Examiner')).toBeInTheDocument()
    expect(screen.getByText('Please wait while we prepare your IELTS test session')).toBeInTheDocument()
  })

  it('does not render when isVisible is false', () => {
    render(
      <ConnectionLoader
        isVisible={false}
        connectionStatus="connecting"
      />
    )

    expect(screen.queryByText('Connecting to Examiner')).not.toBeInTheDocument()
  })

  it('shows all connection steps', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connecting"
      />
    )

    expect(screen.getByText('Getting Connection Details')).toBeInTheDocument()
    expect(screen.getByText('Connecting to Room')).toBeInTheDocument()
    expect(screen.getByText('Enabling Microphone')).toBeInTheDocument()
  })

  it('shows progress bar', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connecting"
      />
    )

    expect(screen.getByText('Connection Progress')).toBeInTheDocument()
    expect(screen.getByText('Establishing...')).toBeInTheDocument()
  })

  it('shows connected status', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connected"
      />
    )

    expect(screen.getByText('Connected!')).toBeInTheDocument()
  })

  it('shows failed status', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="failed"
      />
    )

    expect(screen.getByText('Connection Failed')).toBeInTheDocument()
  })

  it('shows loading spinner when connecting', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connecting"
      />
    )

    // The loading spinner should be present (it's a div with specific classes)
    const spinner = document.querySelector('.w-6.h-6.border-2.border-amber-500.border-t-transparent.rounded-full')
    expect(spinner).toBeInTheDocument()
  })

  it('shows success icon when connected', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connected"
      />
    )

    expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument()
  })

  it('shows error icon when failed', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="failed"
      />
    )

    expect(screen.getByTestId('x-mark-icon')).toBeInTheDocument()
  })

  it('displays step descriptions', () => {
    render(
      <ConnectionLoader
        isVisible={true}
        connectionStatus="connecting"
      />
    )

    expect(screen.getByText('Retrieving secure connection information')).toBeInTheDocument()
    expect(screen.getByText('Establishing secure WebRTC connection')).toBeInTheDocument()
    expect(screen.getByText('Activating audio input for the test')).toBeInTheDocument()
  })
}) 
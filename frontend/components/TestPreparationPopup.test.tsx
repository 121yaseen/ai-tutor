import { render, screen, fireEvent } from '@testing-library/react'
import { TestPreparationPopup } from './TestPreparationPopup'

// Mock the Heroicons components
jest.mock('@heroicons/react/24/outline', () => ({
  CheckCircleIcon: ({ className }: { className?: string }) => (
    <div data-testid="check-circle-icon" className={className} />
  ),
  MicrophoneIcon: ({ className }: { className?: string }) => (
    <div data-testid="microphone-icon" className={className} />
  ),
  SpeakerWaveIcon: ({ className }: { className?: string }) => (
    <div data-testid="speaker-wave-icon" className={className} />
  ),
  HomeIcon: ({ className }: { className?: string }) => (
    <div data-testid="home-icon" className={className} />
  ),
  PencilIcon: ({ className }: { className?: string }) => (
    <div data-testid="pencil-icon" className={className} />
  ),
  XMarkIcon: ({ className }: { className?: string }) => (
    <div data-testid="x-mark-icon" className={className} />
  ),
}))

describe('TestPreparationPopup', () => {
  const mockOnClose = jest.fn()
  const mockOnStartTest = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when isOpen is true', () => {
    render(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    expect(screen.getByText('Test Preparation')).toBeInTheDocument()
    expect(screen.getByText('Ensure optimal conditions for your IELTS test')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    render(
      <TestPreparationPopup
        isOpen={false}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    expect(screen.queryByText('Test Preparation')).not.toBeInTheDocument()
  })

  it('shows all preparation items', () => {
    render(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    expect(screen.getByText('Quiet Environment')).toBeInTheDocument()
    expect(screen.getByText('Microphone Test')).toBeInTheDocument()
    expect(screen.getByText('Speaker/Headphones')).toBeInTheDocument()
    expect(screen.getByText('Pen and Paper')).toBeInTheDocument()
  })

  it('calls onClose when cancel button is clicked', () => {
    render(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    fireEvent.click(screen.getByText('Cancel'))
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('resets checkboxes when popup is closed', () => {
    const { rerender } = render(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    // Check some items
    const checkboxes = screen.getAllByRole('button').filter(button => 
      button.getAttribute('data-testid') !== 'x-mark-icon'
    )
    
    fireEvent.click(checkboxes[0]) // Check first item
    fireEvent.click(checkboxes[1]) // Check second item

    // Close popup
    fireEvent.click(screen.getByText('Cancel'))

    // Reopen popup
    rerender(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    // Verify all checkboxes are unchecked
    const newCheckboxes = screen.getAllByRole('button').filter(button => 
      button.getAttribute('data-testid') !== 'x-mark-icon'
    )
    
    // All checkboxes should be unchecked (no CheckCircleIcon)
    expect(screen.queryByTestId('check-circle-icon')).not.toBeInTheDocument()
  })

  it('calls onStartTest when start test button is clicked and all required items are checked', () => {
    render(
      <TestPreparationPopup
        isOpen={true}
        onClose={mockOnClose}
        onStartTest={mockOnStartTest}
      />
    )

    // Check all required items
    const checkboxes = screen.getAllByRole('button').filter(button => 
      button.getAttribute('data-testid') !== 'x-mark-icon'
    )
    
    // Click the first 3 checkboxes (required items)
    fireEvent.click(checkboxes[0])
    fireEvent.click(checkboxes[1])
    fireEvent.click(checkboxes[2])

    fireEvent.click(screen.getByText('Start Test'))
    expect(mockOnStartTest).toHaveBeenCalledTimes(1)
  })
}) 
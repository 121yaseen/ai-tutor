class PcmRecorderProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super(options);
    // The raw PCM data buffer
    this.buffer = null;
  }

  process(inputs) {
    const input = inputs[0];
    if (input.length > 0) {
      const channelData = input[0];
      if (channelData instanceof Float32Array) {
        // Post the underlying ArrayBuffer
        this.port.postMessage(channelData.buffer, [channelData.buffer]);
      }
    }
    return true;
  }
}

registerProcessor("pcm-recorder-processor", PcmRecorderProcessor);

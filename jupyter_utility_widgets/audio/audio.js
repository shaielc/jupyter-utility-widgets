// Worklet inspired by: https://gist.github.com/tatsuyasusukida/b6daa0cd09bba2fbbf6289c58777eeca
// Loading mechanism from stackoverflow answer:
// https://stackoverflow.com/questions/55412638/audiocontext-audioworklet-addmodule-how-to-load-by-blob

// Load worklet
async function load_recorder_inline(audio_context) {
  let bypass_loading = new Blob(
    [
      `
      class AudioRecorder extends AudioWorkletProcessor {
  
          process (inputs, outputs, parameters) {
          const buffer = []
          const channel = 0
  
          for (let t = 0; t < inputs[0][channel].length; t += 1) {
              buffer.push(inputs[0][channel][t])
          }
  
          if (buffer.length >= 1) {
              this.port.postMessage({buffer})
          }
  
          return true
          }
      }
  
      registerProcessor('audio-recorder', AudioRecorder)
      `,
    ],
    { type: "application/javascript" }
  );

  let reader = new FileReader();
  reader.readAsDataURL(bypass_loading);
  let dataURI = await new Promise((res) => {
    reader.onloadend = function () {
      res(reader.result);
    };
  });
  await audio_context.audioWorklet.addModule(dataURI);
  return;
}

// Utility
// From: https://stackoverflow.com/a/14089496
// one-liner to sum the values in an array
function sum(a){
  return a.reduce(function(a,b){return a+b;},0);
}

// call this with an array of Uint8Array objects
function bufjoin(bufs){
  var lens=bufs.map(function(a){return a.length;});
  var aout=new Float32Array(sum(lens));
  for (var i=0;i<bufs.length;++i){
    var start=sum(lens.slice(0,i));
    aout.set(bufs[i],start); // copy bufs[i] to aout at start position
  }
  return aout;
}

// Draw PCM
function drawBuffer(width, height, context, data) {
  var step = Math.max(Math.ceil(data.length / width),10);
  context.clearRect(0, 0, width, height);
  let margin = 2 / height;
  let range = 2;
  let i, j;
  for (i = 0; i < data.length; i += step) {
    let min = 1;
    let max = -1;
    for (j = 0; j < step; j++) {
      let datum = data[i + j];
      if (min > datum) {
        min = datum;
      }
      if (max < datum) {
        max = datum;
      }
    }
    let bar_length = ((max - min + margin) * height) / (range + margin);
    context.fillRect(i / step, height / 2 - bar_length / 2, 1, bar_length);
  }
}
function drawBars(width, height, context, bars) {
  var step = width / bars.length;
  context.clearRect(0, 0, width, height);
  let margin = 2 / height;
  let range = 2;
  let i, j;
  for (i = 0; i < bars.length; i++) {
    let { min, max } = bars[i];
    let bar_length = ((max - min + margin) * height) / (range + margin);
    context.fillRect(i * step, height / 2 - bar_length / 2, step, bar_length);
  }
}

function canvasDrawBars(canvas, bars) {
  drawBars(canvas.width, canvas.height, canvas.getContext("2d"), bars);
}

function canvasDrawBuffer(canvas, chunk) {
  drawBuffer(canvas.width, canvas.height, canvas.getContext("2d"), chunk);
}

function addBar(width, height, context, i, bar, length) {
  var step = width / length;
  let margin = 2 / height;
  let range = 2;
  let { min, max } = bar;
  let bar_length = ((max - min + margin) * height) / (range + margin);
  let x = Math.floor(i * step)
  context.fillRect(x, height / 2 - bar_length / 2, 1, bar_length);
}

function minFilterDownsample(inputData, inputWidth, inputHeight, outputWidth, outputHeight) {
    const outputData = new Uint8ClampedArray(outputWidth * outputHeight * 4);
    const xRatio = inputWidth / outputWidth;
    const yRatio = inputHeight / outputHeight;
  
    for (let y = 0; y < outputHeight; y++) {
      const yStart = Math.floor(y * yRatio);
      const yEnd = Math.min(Math.ceil((y + 1) * yRatio), inputHeight);
  
      for (let x = 0; x < outputWidth; x++) {
        const xStart = Math.floor(x * xRatio);
        const xEnd = Math.min(Math.ceil((x + 1) * xRatio), inputWidth);
  
        let minR = 255, minG = 255, minB = 255, maxA = 0;
  
        for (let yy = yStart; yy < yEnd; yy++) {
          for (let xx = xStart; xx < xEnd; xx++) {
            const idx = (yy * inputWidth + xx) * 4;
            const r = inputData[idx];
            const g = inputData[idx + 1];
            const b = inputData[idx + 2];
            const a = inputData[idx + 3];
  
            minR = Math.min(minR, r);
            minG = Math.min(minG, g);
            minB = Math.min(minB, b);
            maxA = Math.max(maxA, a);
          }
        }
        
        // *max* Alpha = 0 means, no information!
        if (maxA == 0) {
            minR = 255;
            minG = 255;
            minB = 255;
        }
  
        const outputIdx = (y * outputWidth + x) * 4;
        outputData[outputIdx] = minR;
        outputData[outputIdx + 1] = minG;
        outputData[outputIdx + 2] = minB;
        outputData[outputIdx + 3] = maxA;
      }
    }
  
    return outputData;
  }
  

function  copyImageMaxFilter({source, target, targetWidth=null}) {
    const src_context = source.getContext("2d");
    const trg_context = target.getContext("2d");
    const trg_width = targetWidth ?? target.width

    const image_data = src_context.getImageData(0,0, source.width, source.height)
    const downsampled_data = minFilterDownsample(image_data.data, source.width, source.height, trg_width, target.height)
    const new_image_data = trg_context.createImageData(trg_width, target.height)
    new_image_data.data.set(downsampled_data)
    trg_context.putImageData(new_image_data,0,0)
}

function canvasAddBar(state) {
  let visualizer = state["visualizer"];
  let length = state["visualizer_length"] ?? 1;
  let bars = state["bars"];
  let context = visualizer.getContext("2d");

  if (bars.length == length) {
    length *= 2;
    copyImageMaxFilter( {source: visualizer, target: visualizer, targetWidth: visualizer.width/2})
    context.clearRect(visualizer.width/2, 0, visualizer.width/2, visualizer.height )
    state["visualizer_length"] = length;
  }
  addBar(
    visualizer.width,
    visualizer.height,
    context,
    bars.length - 1,
    bars[bars.length - 1],
    length
  );
}
// ~ draw PCM

// Data handling
function handleChunk(state, chunk, currentTime) {
  if (!state["recording"]) {
    return;
  }
  
  // Save raw audio
  state["result"].push({slice: chunk, time: currentTime});

  // Buffer for visualization
  let buffer = state["chunk"];
  var mergedArray = new Float32Array(chunk.length + buffer.length);
  mergedArray.set(buffer);
  mergedArray.set(chunk, buffer.length);
  state["chunk"] = mergedArray;

  if (state["chunk"].length >= 1024)
  {
    const slice = state["chunk"].slice(0,1024)
    state["chunk"] = state["chunk"].slice(1024, state["chunk"].length)
    state["bars"].push({
      min: Math.min(...slice),
      max: Math.max(...slice),
    });
    canvasAddBar(state);
  }
}

async function requestAudioDevice() {
  try { 
    return await navigator.mediaDevices.getUserMedia(
      // constraints - only audio needed for this app
      {
        audio: true,
      }
    );
  } catch (err) {
    console.error(`The following getUserMedia error occurred: ${err}`);
  }
}

function playRecording(state) {
  if (state["recording"]) {
    return;
  }

  let audio_context = state["audio_context"];
  let out_buffers = audio_context.createBuffer(
    1,
    state["audio"].length,
    audio_context.sampleRate
  );
  const out_buffer = out_buffers.getChannelData(0);

  out_buffer.set(state["audio"]);

  const source = audio_context.createBufferSource();
  source.buffer = out_buffers;
  source.connect(audio_context.destination);

  source.start();
  // TODO: add pause
  // TODO: when playing ends set playing to False
}

function startRecording(state) {
  state["result"] = [];
  state["chunk"] = new Float32Array(0);
  state["recording"] = true;
  state["visualizer_length"] = 1;
  state["bars"] = [];
  let visualizer = state["visualizer"]
  let context = visualizer.getContext("2d")
  context.clearRect(0, 0, visualizer.width, visualizer.height);
}

function stopRecording(state) {
  state["recording"] = false;
  state["audio"] = bufjoin(state["result"].map(v => v.slice))
  state["model"].set("audio", new DataView(state["audio"].buffer));
  state["model"].save_changes()
}

function loadAudio(binary_audio, state) {
  state["audio"] = new Float32Array(binary_audio.buffer)
  canvasDrawBuffer(state["visualizer"], state["audio"])

}

function setupAudioGraph(audio_context, stream, state) {
  const mediaStreamSource = audio_context.createMediaStreamSource(stream);
  const channelSplitter = audio_context.createChannelSplitter(2);
  mediaStreamSource.connect(channelSplitter);

  load_recorder_inline(audio_context).then(() => {
    const audio_recorder = new AudioWorkletNode(
      audio_context,
      "audio-recorder"
    );
    channelSplitter.connect(audio_recorder, 0);
    audio_recorder.port.addEventListener("message", (event) => {
      handleChunk(state, event.data.buffer, audio_context.currentTime);
    });
    audio_recorder.port.start();
    audio_recorder.connect(audio_context.destination);
  });
}
export default async () => {
  let canvas = document.createElement("canvas");
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  let state = {
    chunk: new Float32Array(0),
    result: [],
    bars: [],
    recording: false,
    visualizer: canvas,
    audio_context: null,
    model: null
  };

  return {
    initialize({ model }) {
      let audio_context = new AudioContext();
      state["audio_context"] = audio_context;
      let sampleRate = model.get("sample_rate");
      model.set("sample_rate", audio_context.sampleRate);
      model.save_changes()
      model.send({"type": "resample", "current": sampleRate, "out": audio_context.sampleRate});
      return () => {
        if (state.audio_context) {
          state.audio_context.close();
        }
      };
    },
    render({ model, el }) {
      state['model'] = model
      if (!(navigator.mediaDevices || navigator.mediaDevices.getUserMedia)) {
        el.innerHTML = "Your browser does not support the MediaDevices API";
      }
      let visualizer = state["visualizer"]
      if (!document.body.contains(visualizer))
      {
        el.appendChild(visualizer);
      }
      else {
        let err_element = document.createElement("div")
        err_element.innerHTML = "Displaying the \"Recorder\" widget in multiple locations is currently not supported"
        el.appendChild(err_element)
        return
      }
      
      requestAudioDevice().then((stream) => {
        let audio_context = state["audio_context"];
        setupAudioGraph(audio_context, stream, state);

        state["stream"] = stream;
        state["recording"] = model.get("recording");
        model.on("change:recording", () => {
          model.get("recording")
            ? startRecording(state)
            : stopRecording(state);
        });
        model.on("change:playing", () => {
          model.get("playing") ?
          playRecording(state) :
          null
        });
        model.on("change:audio", () => loadAudio(model.get("audio"), state))
        loadAudio(model.get("audio"), state)

        
      });
    return () => {
    }
    },
  };
};

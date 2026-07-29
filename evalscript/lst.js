//VERSION=3

function setup() {
  return {
    input: ["LST"],
    output: {
      bands: 1,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [
    sample.LST
  ];
}
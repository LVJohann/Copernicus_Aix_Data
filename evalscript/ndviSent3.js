//VERSION=3

function setup() {
    return {
        input: ["NDVI"],
        output: {
            bands: 1,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(sample) {
    return [sample.NDVI];
}
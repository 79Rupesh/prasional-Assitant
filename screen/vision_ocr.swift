import Foundation
import Vision

guard CommandLine.arguments.count > 1 else {
    print("Missing image path")
    exit(1)
}

let imagePath = CommandLine.arguments[1]
let imageURL = URL(fileURLWithPath: imagePath)

let request = VNRecognizeTextRequest()

request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(
    url: imageURL,
    options: [:]
)

do {
    try handler.perform([request])

    let observations = request.results ?? []

    var results: [[String: Any]] = []

    for observation in observations {
        guard let candidate = observation.topCandidates(1).first else {
            continue
        }

        let box = observation.boundingBox

        results.append([
            "text": candidate.string,
            "confidence": candidate.confidence,
            "x": box.origin.x,
            "y": box.origin.y,
            "width": box.width,
            "height": box.height
        ])
    }

    let jsonData = try JSONSerialization.data(
        withJSONObject: results,
        options: []
    )

    print(String(data: jsonData, encoding: .utf8)!)

} catch {
    print("OCR error: \(error)")
    exit(1)
}
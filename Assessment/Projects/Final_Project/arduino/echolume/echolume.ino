#define EIDSP_QUANTIZE_FILTERBANK   0

/* Includes ---------------------------------------------------------------- */
#include <PDM.h>
#include <xms.12138-project-1_inferencing.h>
#include <Adafruit_NeoPixel.h>  // WS2812 LED strip control

// --- WS2812 LED strip configuration ---
#define LED_PIN    2      // WS2812 data line on D2
#define NUM_LEDS   10     // Number of LEDs

// NeoPixel object
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

/** Audio buffers, pointers and selectors */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static signed short sampleBuffer[2048];
static bool debug_nn = false;

enum LampState {
    STATE_OFF,
    STATE_GENERAL,
    STATE_READING,
    STATE_SLEEP
};

LampState current_state = STATE_OFF;
LampState previous_state = STATE_OFF;

unsigned long last_state_change_ms = 0;
const unsigned long STATE_LOCK_DURATION = 1000;

// Confidence threshold (matches EI Model testing setting at 0.6)
const float CONFIDENCE_THRESHOLD = 0.60f;
// ==========================================

// Helper: set all LEDs to a single colour
void setAllLeds(uint8_t r, uint8_t g, uint8_t b) {
    for(int i=0; i<NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show();
}

void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Smart Lamp with 1s State Lock Started.");

    // Initialise LED strip
    strip.begin();
    // Cap overall brightness (0-255) to limit current draw on 3.3V rail
    strip.setBrightness(150);
    strip.show(); // Start with all LEDs off

    run_classifier_init();

    if (microphone_inference_start(EI_CLASSIFIER_SLICE_SIZE) == false) {
        ei_printf("ERR: Could not allocate audio buffer\r\n");
        return;
    }

    ei_printf("\n--- System Ready (Lock active) ---\n");
    ei_printf("Current State: [ OFF ]\n");
}

void loop() {
    bool m = microphone_inference_record();
    if (!m) return;

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_SLICE_SIZE;
    signal.get_data = &microphone_audio_signal_get_data;
    ei_impulse_result_t result = { 0 };

    EI_IMPULSE_ERROR r = run_classifier_continuous(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) return;

    float best_value = 0.0;
    const char* best_label = "";
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        if (result.classification[ix].value > best_value) {
            best_value = result.classification[ix].value;
            best_label = result.classification[ix].label;
        }
    }

    unsigned long now = millis();

    if (best_value >= CONFIDENCE_THRESHOLD) {

        if (now - last_state_change_ms >= STATE_LOCK_DURATION) {

            LampState next_state = current_state;

            if (strcmp(best_label, "turn_on") == 0) {
                if (current_state == STATE_OFF) next_state = STATE_GENERAL;
            }
            else if (strcmp(best_label, "turn_off") == 0) {
                if (current_state != STATE_OFF) next_state = STATE_OFF;
            }
            else if (strcmp(best_label, "reading") == 0) {
                if (current_state != STATE_OFF) next_state = STATE_READING;
            }
            else if (strcmp(best_label, "sleep") == 0) {
                if (current_state != STATE_OFF) next_state = STATE_SLEEP;
            }

            if (next_state != current_state) {
                current_state = next_state;
                last_state_change_ms = now;
            }
        }
    }

    // Update LED colour on state change
    if (current_state != previous_state) {
        switch (current_state) {
            case STATE_OFF:
                ei_printf("Current State: [ OFF ]\n");
                setAllLeds(0, 0, 0); // Lights off
                break;
            case STATE_GENERAL:
                ei_printf("Current State: [ GENERAL MODE ]\n");
                setAllLeds(0, 255, 200); // Ice blue
                break;
            case STATE_READING:
                ei_printf("Current State: [ READING MODE ]\n");
                setAllLeds(255, 255, 255); // Pure white
                break;
            case STATE_SLEEP:
                ei_printf("Current State: [ SLEEP MODE ]\n");
                setAllLeds(255, 50, 0); // Warm orange-red
                break;
        }
        previous_state = current_state;
    }
}

// ---- PDM microphone callbacks (EI library boilerplate) ----
static void pdm_data_ready_inference_callback(void) {
    int bytesAvailable = PDM.available();
    int bytesRead = PDM.read((char *)&sampleBuffer[0], bytesAvailable);
    if (inference.buf_ready == 0) {
        for(int i = 0; i < bytesRead>>1; i++) {
            inference.buffer[inference.buf_count++] = sampleBuffer[i];
            if(inference.buf_count >= inference.n_samples) {
                inference.buf_count = 0; inference.buf_ready = 1; break;
            }
        }
    }
}

static bool microphone_inference_start(uint32_t n_samples) {
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));
    if(inference.buffer == NULL) return false;
    inference.buf_count = 0; inference.n_samples = n_samples; inference.buf_ready = 0;
    PDM.onReceive(&pdm_data_ready_inference_callback);
    PDM.setBufferSize(4096);
    if (!PDM.begin(1, EI_CLASSIFIER_FREQUENCY)) { microphone_inference_end(); return false; }
    PDM.setGain(127);
    return true;
}

static bool microphone_inference_record(void) {
    inference.buf_ready = 0; inference.buf_count = 0;
    while(inference.buf_ready == 0) { delay(1); }
    return true;
}

static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr) {
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);
    return 0;
}

static void microphone_inference_end(void) {
    PDM.end(); free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif

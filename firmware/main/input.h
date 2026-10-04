#pragma once
#include "esp_err.h"

/** Initialisiert MPR121, DRV2605L, Mitteltaste und startet den Eingabe-Task (hohe Priorität). */
esp_err_t input_start(void);

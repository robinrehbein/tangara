/* Machbarkeitstest S31: USB-Host-UAC-Treiber + TinyUSB-Device (MSC) linken. Nur Build. */
#include "usb/usb_host.h"
#include "usb/uac_host.h"
#include "tinyusb_default_config.h"
#include "tinyusb.h"
void app_main(void)
{
    usb_host_config_t hc = {.intr_flags = 0};
    usb_host_install(&hc);
    uac_host_driver_config_t uc = {.create_background_task = true, .task_priority = 5, .stack_size = 4096,
                                   .core_id = 0, .callback = NULL, .callback_arg = NULL};
    uac_host_install(&uc);
    const tinyusb_config_t tc = TINYUSB_DEFAULT_CONFIG();
    tinyusb_driver_install(&tc);
}

#pragma once

#include "concurrency/OSThread.h"
#include "configuration.h" // fw+ 1375: brings in variant.h (HAS_HARDWARE_WATCHDOG) on ESP32 too
#include <stdint.h>

#ifdef HAS_HARDWARE_WATCHDOG
class WatchdogThread : private concurrency::OSThread
{
  public:
    WatchdogThread();
    void feedDog(void);
    virtual bool setup();
    virtual int32_t runOnce() override;
};

extern WatchdogThread *watchdogThread;
#endif

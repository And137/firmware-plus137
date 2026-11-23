#include "watchdogThread.h"
#include "configuration.h"

#ifdef HAS_HARDWARE_WATCHDOG
WatchdogThread *watchdogThread;

WatchdogThread::WatchdogThread() : OSThread("Watchdog")
{
    setup();
}

void WatchdogThread::feedDog(void)
{
    digitalWrite(HARDWARE_WATCHDOG_DONE, HIGH);
    delay(1);
    digitalWrite(HARDWARE_WATCHDOG_DONE, LOW);
}

int32_t WatchdogThread::runOnce()
{
#if HARDWARE_WATCHDOG_TIMEOUT_MS >= 10000 // fw+: no log line for the 1 s heartbeat feeds
    LOG_DEBUG("Feeding hardware watchdog");
#endif
    feedDog();
    return HARDWARE_WATCHDOG_TIMEOUT_MS;
}

bool WatchdogThread::setup()
{
    LOG_DEBUG("init hardware watchdog");
#ifdef HARDWARE_WATCHDOG_WAKE // fw+: optional, the WSL V3 heartbeat has no wake line
    pinMode(HARDWARE_WATCHDOG_WAKE, INPUT);
#endif
    pinMode(HARDWARE_WATCHDOG_DONE, OUTPUT);
    delay(1);
    digitalWrite(HARDWARE_WATCHDOG_DONE, LOW);
    delay(1);
    feedDog();
    return true;
}
#endif
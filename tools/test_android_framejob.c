// Regression for the Android guest-address shift and the partial frame-job finish race.
// Runs on a Linux CI host, with and without __ANDROID__ to exercise both address layouts.
// Uses actual hook_id() and rt_frame_job_kickoff() from the runtime; no game files required.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../runtime/hle/hooks.c"
#include "../runtime/hle/delegate_null.c"

const GameAddrs *g_ga;

static uint64_t clock_ns;
static int slept;
static uint64_t active_job;
uint64_t plat_now_ns(void) { return clock_ns += 1000; }
void plat_sleep_until_ns(uint64_t when) {
    clock_ns = when;
    ++slept;
    if (active_job && slept == 1)
        *(uint64_t *)(uintptr_t)(active_job + 0x10) = 0; // finish's second store
}

int main(void) {
    GameAddrs addresses = {0};
    g_ga = &addresses;
    const size_t n = sizeof hook_field / sizeof hook_field[0];
    for (size_t i = 0; i < n; ++i) {
        uint64_t *field = (uint64_t *)((char *)&addresses + hook_field[i]);
        *field = 0x7000001000ull + i * 0x10;
    }
    for (size_t i = 0; i < n; ++i) {
        uint64_t original = *(uint64_t *)((char *)&addresses + hook_field[i]);
        assert(hook_id(original - GA_SHIFT) == (int)i);
    }
    assert(hook_id(0x4000) == -1);

    // A frame that has set the base vtable but still has a delegate
    // must wait: the worker's pending clear would otherwise erase the
    // next frame's freshly installed delegate.
    addresses.DELEGATE_JOB_VTABLE_LIVE = 0x7001c51308ull;
    addresses.DELEGATE_JOB_VTABLE_BASE = 0x7001c51358ull;
    unsigned char area[0x400] __attribute__((aligned(16))) = {0};
    uint64_t owner = (uint64_t)(uintptr_t)area;
    uint64_t job = owner + 0xc8;
    *(uint8_t *)(uintptr_t)(owner + 0x1d8) = 1; // previous run done
    *(uint64_t *)(uintptr_t)job = GA(DELEGATE_JOB_VTABLE_BASE);
    *(uint64_t *)(uintptr_t)(job + 0x10) = 0x1234; // not cleared yet
    *(uint64_t *)(uintptr_t)(job + 0x28) = owner;
    active_job = job;
    rt_frame_job_kickoff(owner);
    assert(slept == 1);
    assert(*(uint64_t *)(uintptr_t)(job + 0x10) == 0);
    active_job = 0;

    // An already completed job should not wait.
    slept = 0;
    rt_frame_job_kickoff(owner);
    assert(slept == 0);
    puts("Hook shift and partial-finish synchronization: PASS");
    return 0;
}

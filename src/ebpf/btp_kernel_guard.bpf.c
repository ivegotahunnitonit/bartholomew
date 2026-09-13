// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
/* Copyright (c) 2026 Bartholomew Systems Laboratory */
/* BTP Kernel Guard - eBPF Syscall Interceptor for Autonomous AI Agents */

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_PATH_LEN 256
#define MAX_COMMAND_LEN 128
#define ACTION_ALLOW 0
#define ACTION_DENY 1
#define ACTION_NOTIFY 2

/* Event structure passed from kernel ring buffer to BTP userspace daemon */
struct btp_kernel_event {
    __u32 pid;
    __u32 uid;
    __u32 syscall_nr;
    __u32 action;
    char comm[16];
    char target[MAX_PATH_LEN];
    __u64 timestamp_ns;
};

/* BPF Ring Buffer for high-throughput zero-copy event streaming */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); /* 256 KB ring buffer */
} btp_events SEC(".maps");

/* BPF Hash Map of monitored agent worker PIDs */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);   /* PID */
    __type(value, __u32); /* Policy flags */
} monitored_agent_pids SEC(".maps");

/* Tracepoint: sys_enter_execve - Gate command executions */
SEC("tracepoint/syscalls/sys_enter_execve")
int tracepoint_syscalls_sys_enter_execve(struct trace_event_raw_sys_enter *ctx)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    /* Verify if the current process is a monitored autonomous agent worker */
    __u32 *policy_flags = bpf_map_lookup_elem(&monitored_agent_pids, &pid);
    if (!policy_flags) {
        return 0; /* Unmonitored process, allow through */
    }

    struct btp_kernel_event *event;
    event = bpf_ringbuf_reserve(&btp_events, sizeof(*event), 0);
    if (!event) {
        return 0;
    }

    event->pid = pid;
    event->uid = bpf_get_current_uid_gid();
    event->syscall_nr = 59; /* __NR_execve on x86_64 */
    event->action = ACTION_NOTIFY;
    event->timestamp_ns = bpf_ktime_get_ns();
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    /* Read binary filename pointer from first syscall argument */
    const char *filename_ptr = (const char *)ctx->args[0];
    bpf_probe_read_user_str(&event->target, sizeof(event->target), filename_ptr);

    /* Submit event to userspace ring buffer */
    bpf_ringbuf_submit(event, 0);

    return 0;
}

/* Tracepoint: sys_enter_unlinkat - Gate file deletions */
SEC("tracepoint/syscalls/sys_enter_unlinkat")
int tracepoint_syscalls_sys_enter_unlinkat(struct trace_event_raw_sys_enter *ctx)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;

    __u32 *policy_flags = bpf_map_lookup_elem(&monitored_agent_pids, &pid);
    if (!policy_flags) {
        return 0;
    }

    struct btp_kernel_event *event;
    event = bpf_ringbuf_reserve(&btp_events, sizeof(*event), 0);
    if (!event) {
        return 0;
    }

    event->pid = pid;
    event->uid = bpf_get_current_uid_gid();
    event->syscall_nr = 263; /* __NR_unlinkat on x86_64 */
    event->action = ACTION_NOTIFY;
    event->timestamp_ns = bpf_ktime_get_ns();
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    const char *pathname_ptr = (const char *)ctx->args[1];
    bpf_probe_read_user_str(&event->target, sizeof(event->target), pathname_ptr);

    bpf_ringbuf_submit(event, 0);

    return 0;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";

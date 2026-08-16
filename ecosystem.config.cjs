module.exports = {
  apps: [{
    name: 'acn-node',
    script: 'src/index.ts',
    interpreter: 'node',
    interpreter_args: '--experimental-strip-types',
    cwd: '/opt/acn',
    instances: 1,
    exec_mode: 'fork',
    max_memory_restart: '512M',
    restart_delay: 2000,
    max_restarts: 20,
    min_uptime: '10s',
    env: {
      NODE_ENV: 'production',
      PORT: '8080',
    },
    env_file: '/opt/acn/.env',
    out_file: '/var/log/acn/out.log',
    error_file: '/var/log/acn/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
  }]
};

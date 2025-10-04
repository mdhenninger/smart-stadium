import clsx from 'clsx';
import { Card } from './Card';
import { Loader } from './feedback/Loader';
import { useDefaultLighting, useDeviceTest, useDevices, useToggleDevice } from '../hooks/useDevices';
import { formatTimestamp } from '../lib/time';

export const DevicePanel = () => {
  const { data, isLoading, isError, refetch } = useDevices();
  const toggle = useToggleDevice();
  const tester = useDeviceTest();
  const defaultLighting = useDefaultLighting();

  const mutationDeviceId = (toggle.variables as { deviceId?: string } | undefined)?.deviceId;
  const testDeviceId = tester.variables;

  return (
    <Card
      title="Smart lights"
      subtitle={data ? `${data.summary.online_devices}/${data.summary.total_devices} online` : undefined}
      action={
        <button
          type="button"
          className="btn"
          onClick={() => defaultLighting.mutate()}
          disabled={defaultLighting.isPending}
        >
          {defaultLighting.isPending ? 'Saving…' : 'Default lighting'}
        </button>
      }
    >
      {isLoading ? (
        <div className="panel-empty">
          <Loader />
          <span>Loading devices…</span>
        </div>
      ) : null}
      {isError ? (
        <div className="panel-empty panel-empty--error">
          <span>Could not load devices.</span>
          <button type="button" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      ) : null}
      {!isLoading && !isError && data ? (
        <ul className="device-list">
          {data.devices.map((device) => {
            const toggling = toggle.isPending && mutationDeviceId === device.device_id;
            const testing = tester.isPending && testDeviceId === device.device_id;
            return (
              <li key={device.device_id} className="device-row">
                <div className="device-row__main">
                  <span className="device-row__name">{device.name}</span>
                  <span className={clsx('device-row__status', `device-row__status--${device.status}`)}>
                    {device.status}
                  </span>
                </div>
                <div className="device-row__meta">
                  <span>{device.ip_address}</span>
                  <span>Last seen {formatTimestamp(device.last_seen ?? null)}</span>
                </div>
                <div className="device-row__actions">
                  <button
                    type="button"
                    className={device.enabled ? 'btn btn--ghost' : 'btn btn--primary'}
                    onClick={() => toggle.mutate({ deviceId: device.device_id, enabled: !device.enabled })}
                    disabled={toggling}
                  >
                    {toggling ? 'Updating…' : device.enabled ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={() => tester.mutate(device.device_id)}
                    disabled={testing}
                  >
                    {testing ? 'Testing…' : 'Test'}
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      ) : null}
    </Card>
  );
};

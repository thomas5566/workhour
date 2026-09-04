import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import MssqlMonitoring, { formatMetric } from '@/components/MssqlMonitoring.vue';

describe('MSSQL monitoring', () => {
  it('formats service, database, backup and log metrics', () => {
    expect(formatMetric({ key: 'service', value: 1, status: 'ok' })).toBe('執行中');
    expect(formatMetric({ key: 'db.state', value: 0, status: 'ok' })).toBe('ONLINE');
    expect(formatMetric({ key: 'db.state', value: 6, status: 'critical' })).toBe('OFFLINE');
    expect(formatMetric({ value: 3660, units: 's', status: 'ok' })).toBe('1 小時 1 分');
    expect(formatMetric({ value: 95, units: '%', status: 'critical' })).toBe('95%');
  });
  it.each(['stale', 'unsupported', 'unknown'])('does not show old healthy data for %s', (status) => {
    expect(formatMetric({ key: 'service', value: 1, status })).toBe('—');
  });
  it('renders severity and sample time with text, not just color', () => {
    const wrapper = mount(MssqlMonitoring, { props: { servers: [{
      host_id: '1', host_name: 'WIN-TEST', name: 'POS303', instance: 'pos3030', status: 'degraded',
      problems: [{ event_id: '5', severity_label: 'High', message: 'Log usage high' }],
      metrics: [{ item_id: '1', label: 'whmis Log', key: 'db.logused', value: 95, units: '%',
        status: 'critical', sampled_at: '2026-09-02T00:00:00Z' }],
    }] } });
    expect(wrapper.find('.metric.critical').text()).toContain('95%');
    expect(wrapper.text()).toContain('取樣：');
    expect(wrapper.text()).toContain('1 筆未恢復警告');
    wrapper.unmount();
  });
  it('distinguishes API errors from an empty inventory', () => {
    const wrapper = mount(MssqlMonitoring, { props: { error: 'MSSQL monitoring API failed' } });
    expect(wrapper.get('[role="alert"]').text()).toContain('API failed');
    expect(wrapper.text()).not.toContain('沒有可讀取');
    wrapper.unmount();
  });
});

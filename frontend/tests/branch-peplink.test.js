import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BranchPeplinkMonitoring from '@/components/BranchPeplinkMonitoring.vue';

function device(number) {
  return { host_id: String(number), name: `Peplink-${String(number).padStart(2, '0')}`,
    host_name: `Peplink-${String(number).padStart(2, '0')}`, ip_address: `192.0.2.${number}`,
    status: 'ok', message: 'SNMP 可用',
    metrics: { cpu: 25, memory: null, uptime_seconds: 90000, 'WAN 1 狀態': 'Connected', 'WAN 1 健康檢查': 'Success' },
    metric_states: { cpu: 'ok', memory: 'missing', uptime_seconds: 'ok', 'WAN 1 狀態': 'ok', 'WAN 1 健康檢查': 'ok' },
    metric_sampled_at: {},
  };
}

describe('branch Peplink page', () => {
  it('paginates 91 hosts and retains search/page on background refresh', async () => {
    const devices = Array.from({ length: 91 }, (_, i) => device(i + 1));
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices } });
    expect(wrapper.findAll('article')).toHaveLength(12);
    await wrapper.findAll('button')[1].trigger('click');
    expect(wrapper.find('h3').text()).toBe('Peplink-13');
    await wrapper.setProps({ devices: devices.map(row => ({ ...row })) });
    expect(wrapper.find('h3').text()).toBe('Peplink-13');
    await wrapper.find('input').setValue('Peplink-91');
    expect(wrapper.findAll('article')).toHaveLength(1);
    expect(wrapper.find('h3').text()).toBe('Peplink-91');
    expect(wrapper.text()).toContain('第 1 / 1 頁');
    wrapper.unmount();
  });
  it('shows missing resource data and colors WAN status', () => {
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [device(1)] } });
    expect(wrapper.text()).toContain('尚未提供');
    expect(wrapper.text()).toContain('25%');
    expect(wrapper.findAll('td.good')).toHaveLength(2);
    wrapper.unmount();
  });
  it('renders disconnected links red but disabled health checks neutral', () => {
    const row = device(1);
    row.metrics['WAN 1 狀態'] = 'Disconnect';
    row.metrics['WAN 1 健康檢查'] = 'Fail';
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [row] } });
    expect(wrapper.findAll('td.bad')).toHaveLength(2);
    expect(wrapper.vm.wanClass({ ...row, metrics: { ...row.metrics, 'WAN 1 狀態': 'Disable' } }, 'WAN 1', '健康檢查')).toBe('neutral');
    wrapper.unmount();
  });
  it('distinguishes permissions or empty scope from API failure', () => {
    const wrapper = mount(BranchPeplinkMonitoring);
    expect(wrapper.text()).toContain('Read 權限');
    wrapper.unmount();
    const failed = mount(BranchPeplinkMonitoring, { props: { error: 'API unavailable' } });
    expect(failed.get('[role="alert"]').text()).toBe('API unavailable');
    failed.unmount();
  });
  it('colors backup standby green and disabled red, and hides wifi WANs', () => {
    const row = device(1);
    for (const [wan, state] of [['FET', 'Disable'], ['Cellular', 'Standby'],
      ['Wi-Fi WAN', 'Disconnect'], ['Wi-Fi WAN on 2.4 GHz', 'Disconnect'],
      ['Wi-Fi WAN on 5 GHz', 'Disconnect'], ['VLAN WAN', 'Disconnect'], ['VLAN WAN 2', 'Disconnect']]) {
      row.metrics[`${wan} 狀態`] = state;
      row.metric_states[`${wan} 狀態`] = 'ok';
    }
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [row] } });
    expect(wrapper.findAll('tbody tr')).toHaveLength(3);
    expect(wrapper.find('td.bad').text()).toContain('Disable');
    expect(wrapper.findAll('td.good').some(cell => cell.text().includes('Standby'))).toBe(true);
    expect(wrapper.find('table').text()).not.toContain('Wi-Fi');
    expect(wrapper.find('table').text()).not.toContain('VLAN');
    wrapper.unmount();
  });
  it('adds a newly discovered host during refresh without losing the filter', async () => {
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [device(1)] } });
    await wrapper.find('input').setValue('Peplink-202');
    expect(wrapper.findAll('article')).toHaveLength(0);
    await wrapper.setProps({ devices: [device(1), device(202)] });
    expect(wrapper.find('h3').text()).toBe('Peplink-202');
    expect(wrapper.find('input').element.value).toBe('Peplink-202');
    wrapper.unmount();
  });
  it('colors uptime only above 90 days and clears it after recovery', async () => {
    const row = device(1);
    row.metrics.uptime_seconds = 90 * 86400;
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [row] } });
    expect(wrapper.findAll('.resources > div')[2].classes()).toContain('metric-healthy');
    await wrapper.setProps({ devices: [{ ...row, alert_severity: 2,
      metrics: { ...row.metrics, uptime_seconds: 90 * 86400 + 1 },
      metric_severities: { uptime_seconds: 2 } }] });
    expect(wrapper.findAll('.resources > div')[2].classes()).toContain('metric-warning');
    expect(wrapper.find('article header').text()).toContain('Warning');
    await wrapper.setProps({ devices: [row] });
    expect(wrapper.findAll('.resources > div')[2].classes()).toContain('metric-healthy');
    wrapper.unmount();
  });
  it('shows critical badge and keeps disconnect red with a Warning event', () => {
    const row = device(1);
    row.alert_severity = 4;
    row.metric_severities = { cpu: 4, 'WAN 1 狀態': 2 };
    row.metrics['WAN 1 狀態'] = 'Disconnect';
    const wrapper = mount(BranchPeplinkMonitoring, { props: { devices: [row] } });
    expect(wrapper.find('article header .bad').text()).toBe('Critical');
    expect(wrapper.findAll('.resources > div')[0].classes()).toContain('metric-critical');
    expect(wrapper.find('td.bad').text()).toContain('Disconnect');
    wrapper.unmount();
  });
});

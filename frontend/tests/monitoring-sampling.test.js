import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MonitoringSampleTime from '@/components/MonitoringSampleTime.vue';

describe('Zabbix sampling timestamp', () => {
  it('shows missing samples instead of fabricating a refresh timestamp', () => {
    const wrapper = mount(MonitoringSampleTime);
    expect(wrapper.text()).toContain('尚無取樣資料');
    expect(wrapper.classes()).toContain('sample-warning');
  });
  it('updates freshness with background snapshots and retains the sample time', async () => {
    const wrapper = mount(MonitoringSampleTime, { props: {
      sampledAt: '2026-09-03T01:00:00Z', referenceTime: '2026-09-03T01:10:00Z',
      label: 'Zabbix 最新指標取樣',
    } });
    expect(wrapper.classes()).not.toContain('sample-warning');
    const formatted = wrapper.vm.formatted;
    await wrapper.setProps({ referenceTime: '2026-09-03T01:10:01Z' });
    expect(wrapper.text()).toContain('逾 10 分鐘無新取樣');
    expect(wrapper.vm.formatted).toBe(formatted);
    await wrapper.setProps({ sampledAt: '2026-09-03T01:10:01Z' });
    expect(wrapper.classes()).not.toContain('sample-warning');
  });
});

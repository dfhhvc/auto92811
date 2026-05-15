import React from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native'

export default function DashboardScreen(): React.JSX.Element {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scroll}>
        <Text style={styles.title}>AutoIncome</Text>
        <Text style={styles.subtitle}>AI驱动的被动收入聚合器</Text>

        <View style={styles.statsRow}>
          <StatCard label="今日扫描" value="128" />
          <StatCard label="有效机会" value="42" />
        </View>

        <TouchableOpacity style={styles.scanButton}>
          <Text style={styles.scanButtonText}>立即扫描</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  scroll: { padding: 20 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#e2e8f0', marginBottom: 4 },
  subtitle: { fontSize: 14, color: '#94a3b8', marginBottom: 24 },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  statCard: {
    flex: 1,
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  statValue: { fontSize: 24, fontWeight: 'bold', color: '#e2e8f0', marginBottom: 4 },
  statLabel: { fontSize: 12, color: '#64748b' },
  scanButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  scanButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
})
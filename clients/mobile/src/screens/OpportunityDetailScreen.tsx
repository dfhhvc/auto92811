import React from 'react'
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
} from 'react-native'

export default function OpportunityDetailScreen({ route, navigation }: any): React.JSX.Element {
  const { id } = route.params

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scroll}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← 返回</Text>
        </TouchableOpacity>
        <Text style={styles.title}>机会详情 #{id}</Text>
        <Text style={styles.description}>
          AI正在分析该机会的详细信息...
        </Text>
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  scroll: { padding: 20 },
  backText: { color: '#60a5fa', fontSize: 16, marginBottom: 16 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#e2e8f0', marginBottom: 12 },
  description: { fontSize: 14, color: '#94a3b8', lineHeight: 22 },
})
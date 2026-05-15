import React from 'react'
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native'

const MOCK_DATA = [
  { id: '1', title: 'AI写作助手代运营', score: 8.5, source: 'V2EX' },
  { id: '2', title: '开源项目GitHub Sponsors', score: 7.8, source: 'GitHub' },
  { id: '3', title: '技术专栏付费订阅', score: 8.2, source: '知乎' },
]

export default function OpportunitiesScreen({ navigation }: any): React.JSX.Element {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>机会探索</Text>
      <FlatList
        data={MOCK_DATA}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('OpportunityDetail', { id: item.id })}
          >
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle} numberOfLines={2}>
                {item.title}
              </Text>
              <View style={styles.scoreBadge}>
                <Text style={styles.scoreText}>{item.score.toFixed(1)}</Text>
              </View>
            </View>
            <Text style={styles.cardSource}>{item.source}</Text>
          </TouchableOpacity>
        )}
      />
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#e2e8f0', padding: 16 },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  cardTitle: { flex: 1, fontSize: 16, fontWeight: '600', color: '#e2e8f0', marginRight: 12 },
  scoreBadge: {
    backgroundColor: 'rgba(59,130,246,0.2)',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: 'rgba(59,130,246,0.4)',
  },
  scoreText: { color: '#60a5fa', fontWeight: '700', fontSize: 14 },
  cardSource: { fontSize: 12, color: '#64748b' },
})
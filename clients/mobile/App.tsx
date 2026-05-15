import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import DashboardScreen from './src/screens/DashboardScreen'
import OpportunitiesScreen from './src/screens/OpportunitiesScreen'
import OpportunityDetailScreen from './src/screens/OpportunityDetailScreen'
import ProfileScreen from './src/screens/ProfileScreen'

const Tab = createBottomTabNavigator()
const Stack = createNativeStackNavigator()

const queryClient = new QueryClient()

function OpportunitiesStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="OpportunitiesList" component={OpportunitiesScreen} />
      <Stack.Screen name="OpportunityDetail" component={OpportunityDetailScreen} />
    </Stack.Navigator>
  )
}

function App(): React.JSX.Element {
  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={{
              headerShown: false,
              tabBarStyle: { backgroundColor: '#0f172a', borderTopColor: '#334155' },
              tabBarActiveTintColor: '#3b82f6',
              tabBarInactiveTintColor: '#64748b',
            }}
          >
            <Tab.Screen
              name="Dashboard"
              component={DashboardScreen}
              options={{ title: '首页' }}
            />
            <Tab.Screen
              name="Opportunities"
              component={OpportunitiesStack}
              options={{ title: '机会' }}
            />
            <Tab.Screen
              name="Profile"
              component={ProfileScreen}
              options={{ title: '我的' }}
            />
          </Tab.Navigator>
        </NavigationContainer>
      </QueryClientProvider>
    </SafeAreaProvider>
  )
}

export default App
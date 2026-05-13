import { useState, useEffect, useCallback } from "react";
import {
  View, Text, Switch, TouchableOpacity,
  ScrollView, RefreshControl, StyleSheet, Alert,
} from "react-native";
import { api } from "@/lib/api";

export default function DashboardScreen() {
  const [active, setActive] = useState(false);
  const [todayCount, setTodayCount] = useState(0);
  const [recentReplies, setRecentReplies] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const profile = await api.getProfile();
      setActive(profile.active ?? false);
      const msgs = await api.getMessages();
      const today = new Date().toDateString();
      const todayMsgs = (msgs.messages ?? []).filter(
        (m: any) => new Date(m.created_at).toDateString() === today && m.ai_generated
      );
      setTodayCount(todayMsgs.length);
      setRecentReplies(todayMsgs.slice(0, 5));
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const onRefresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  const toggleGhost = async (val: boolean) => {
    try {
      await api.toggle(val);
      setActive(val);
    } catch {
      Alert.alert("Error", "Could not toggle Ghost — is backend running?");
    }
  };

  return (
    <ScrollView
      style={s.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#a855f7" />}
    >
      {/* Hero toggle */}
      <View style={s.hero}>
        <Text style={s.heroEmoji}>👻</Text>
        <Text style={s.heroTitle}>Ghost is {active ? "ON" : "OFF"}</Text>
        <Text style={s.heroSub}>
          {active ? "Replying as you right now" : "Tap to activate"}
        </Text>
        <Switch
          value={active}
          onValueChange={toggleGhost}
          trackColor={{ false: "#333", true: "#a855f7" }}
          thumbColor="#fff"
          style={{ transform: [{ scaleX: 1.4 }, { scaleY: 1.4 }], marginTop: 16 }}
        />
      </View>

      {/* Stats */}
      <View style={s.statsRow}>
        <View style={s.stat}>
          <Text style={s.statNum}>{todayCount}</Text>
          <Text style={s.statLabel}>Replied today</Text>
        </View>
      </View>

      {/* Recent activity */}
      <Text style={s.sectionTitle}>Recent replies</Text>
      {recentReplies.length === 0 && (
        <Text style={s.empty}>No replies yet today</Text>
      )}
      {recentReplies.map((msg) => (
        <View key={msg.id} style={s.replyCard}>
          <Text style={s.replyPhone}>{msg.contact_phone}</Text>
          <Text style={s.replyText} numberOfLines={2}>{msg.text}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0a0a0a" },
  hero: { alignItems: "center", paddingVertical: 48, paddingHorizontal: 24 },
  heroEmoji: { fontSize: 64 },
  heroTitle: { color: "#fff", fontSize: 28, fontWeight: "700", marginTop: 12 },
  heroSub: { color: "#888", fontSize: 15, marginTop: 6 },
  statsRow: { flexDirection: "row", justifyContent: "center", paddingHorizontal: 24, marginBottom: 24 },
  stat: { alignItems: "center", backgroundColor: "#111", borderRadius: 16, padding: 20, minWidth: 120 },
  statNum: { color: "#a855f7", fontSize: 36, fontWeight: "800" },
  statLabel: { color: "#888", fontSize: 13, marginTop: 4 },
  sectionTitle: { color: "#fff", fontSize: 17, fontWeight: "600", paddingHorizontal: 24, marginBottom: 12 },
  empty: { color: "#555", paddingHorizontal: 24, fontSize: 14 },
  replyCard: { backgroundColor: "#111", marginHorizontal: 16, marginBottom: 8, borderRadius: 12, padding: 14 },
  replyPhone: { color: "#a855f7", fontSize: 12, marginBottom: 4 },
  replyText: { color: "#ccc", fontSize: 14 },
});

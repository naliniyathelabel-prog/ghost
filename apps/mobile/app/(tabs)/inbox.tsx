import { useState, useEffect, useCallback } from "react";
import {
  View, Text, FlatList, TouchableOpacity,
  RefreshControl, StyleSheet, Alert,
} from "react-native";
import { api } from "@/lib/api";

type Message = {
  id: string;
  contact_phone: string;
  direction: "inbound" | "outbound";
  text: string;
  ai_generated: boolean;
  rating: 1 | -1 | null;
  created_at: string;
};

export default function InboxScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await api.getMessages();
      setMessages(r.messages ?? []);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);
  const onRefresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  const rate = async (id: string, rating: 1 | -1) => {
    try {
      await api.rateMessage(id, rating);
      setMessages((prev) => prev.map((m) => m.id === id ? { ...m, rating } : m));
    } catch { Alert.alert("Error", "Could not rate message"); }
  };

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[s.card, item.direction === "outbound" ? s.outbound : s.inbound]}>
      <View style={s.cardHeader}>
        <Text style={s.phone}>{item.contact_phone}</Text>
        <Text style={s.meta}>
          {item.direction === "outbound" && item.ai_generated ? "👻 Ghost replied" : "received"}
          {"  "}{new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </Text>
      </View>
      <Text style={s.text}>{item.text}</Text>
      {item.ai_generated && (
        <View style={s.ratingRow}>
          <TouchableOpacity onPress={() => rate(item.id, 1)} style={s.ratingBtn}>
            <Text style={[s.ratingIcon, item.rating === 1 && s.ratingActive]}>👍</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={() => rate(item.id, -1)} style={s.ratingBtn}>
            <Text style={[s.ratingIcon, item.rating === -1 && s.ratingActive]}>👎</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  return (
    <FlatList
      style={s.container}
      data={messages}
      keyExtractor={(m) => m.id}
      renderItem={renderItem}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#a855f7" />}
      ListEmptyComponent={<Text style={s.empty}>No messages yet — activate Ghost first</Text>}
      contentContainerStyle={{ padding: 16 }}
    />
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0a0a0a" },
  card: { borderRadius: 14, padding: 14, marginBottom: 10 },
  inbound: { backgroundColor: "#111" },
  outbound: { backgroundColor: "#1a0f2e", borderLeftWidth: 3, borderLeftColor: "#a855f7" },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  phone: { color: "#a855f7", fontSize: 12, fontWeight: "600" },
  meta: { color: "#555", fontSize: 11 },
  text: { color: "#ddd", fontSize: 14, lineHeight: 20 },
  ratingRow: { flexDirection: "row", marginTop: 10, gap: 8 },
  ratingBtn: { padding: 4 },
  ratingIcon: { fontSize: 18, opacity: 0.4 },
  ratingActive: { opacity: 1 },
  empty: { color: "#555", textAlign: "center", marginTop: 60, fontSize: 15 },
});

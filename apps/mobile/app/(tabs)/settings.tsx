import { useState, useEffect } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  ScrollView, StyleSheet, Alert, ActivityIndicator,
} from "react-native";
import { api } from "@/lib/api";

const TONES = ["casual", "formal", "hinglish"];
const LANGS = ["english", "tamil", "hinglish", "mixed"];

export default function TrainScreen() {
  const [name, setName] = useState("");
  const [tone, setTone] = useState("casual");
  const [language, setLanguage] = useState("english");
  const [description, setDescription] = useState("");
  const [samples, setSamples] = useState(["", "", "", "", ""]);
  const [customInstructions, setCustomInstructions] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getProfile()
      .then((p) => {
        setName(p.name ?? "");
        setTone(p.tone ?? "casual");
        setLanguage(p.language ?? "english");
        setDescription(p.description ?? "");
        const s = p.sample_replies ?? [];
        setSamples([...s, ...Array(5).fill("")].slice(0, 5));
        setCustomInstructions(p.custom_instructions ?? "");
      })
      .catch(() => {});
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await api.updateProfile({
        name, tone, language, description,
        sample_replies: samples.filter(Boolean),
        custom_instructions: customInstructions,
      });
      Alert.alert("Saved", "Your Ghost has been trained!");
    } catch {
      Alert.alert("Error", "Could not save — is backend running?");
    } finally {
      setSaving(false);
    }
  };

  const Chip = ({ label, selected, onPress }: any) => (
    <TouchableOpacity style={[s.chip, selected && s.chipActive]} onPress={onPress}>
      <Text style={[s.chipText, selected && s.chipTextActive]}>{label}</Text>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={s.container} contentContainerStyle={{ padding: 20, paddingBottom: 48 }}>
      <Text style={s.heading}>Train Your Ghost</Text>
      <Text style={s.sub}>Paste 5 real replies — Ghost learns your style in 2 minutes.</Text>

      <Text style={s.label}>Your name</Text>
      <TextInput style={s.input} value={name} onChangeText={setName}
        placeholder="e.g. Naliniya" placeholderTextColor="#555" />

      <Text style={s.label}>What do you do?</Text>
      <TextInput style={s.input} value={description} onChangeText={setDescription}
        placeholder="e.g. shop owner, freelance dev, student" placeholderTextColor="#555" />

      <Text style={s.label}>Tone</Text>
      <View style={s.chips}>
        {TONES.map((t) => <Chip key={t} label={t} selected={tone === t} onPress={() => setTone(t)} />)}
      </View>

      <Text style={s.label}>Language style</Text>
      <View style={s.chips}>
        {LANGS.map((l) => <Chip key={l} label={l} selected={language === l} onPress={() => setLanguage(l)} />)}
      </View>

      <Text style={s.label}>5 real replies you have sent before</Text>
      <Text style={s.sublabel}>Ghost will match your exact style from these</Text>
      {samples.map((sv, i) => (
        <TextInput
          key={i} style={s.input} value={sv} multiline
          onChangeText={(v) => setSamples((prev) => prev.map((x, j) => j === i ? v : x))}
          placeholder={"Reply " + (i + 1) + "..."} placeholderTextColor="#555"
        />
      ))}

      <Text style={s.label}>Extra instructions (optional)</Text>
      <TextInput style={[s.input, { height: 90 }]} value={customInstructions}
        onChangeText={setCustomInstructions} multiline
        placeholder="e.g. Never discuss pricing over WhatsApp, always say call me"
        placeholderTextColor="#555" />

      <TouchableOpacity style={s.saveBtn} onPress={save} disabled={saving}>
        {saving
          ? <ActivityIndicator color="#fff" />
          : <Text style={s.saveBtnText}>Save and Train Ghost</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0a0a0a" },
  heading: { color: "#fff", fontSize: 24, fontWeight: "700", marginBottom: 6 },
  sub: { color: "#888", fontSize: 14, marginBottom: 24 },
  label: { color: "#ccc", fontSize: 14, fontWeight: "600", marginBottom: 6, marginTop: 16 },
  sublabel: { color: "#666", fontSize: 12, marginBottom: 8, marginTop: -4 },
  input: { backgroundColor: "#111", color: "#fff", borderRadius: 10, padding: 12,
    fontSize: 14, marginBottom: 8, borderWidth: 1, borderColor: "#222" },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 4 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20,
    backgroundColor: "#111", borderWidth: 1, borderColor: "#333" },
  chipActive: { backgroundColor: "#a855f7", borderColor: "#a855f7" },
  chipText: { color: "#888", fontSize: 13 },
  chipTextActive: { color: "#fff", fontWeight: "600" },
  saveBtn: { backgroundColor: "#a855f7", borderRadius: 14, padding: 16,
    alignItems: "center", marginTop: 24 },
  saveBtnText: { color: "#fff", fontWeight: "700", fontSize: 16 },
});

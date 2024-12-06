import React, {useState} from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, TextInput, Image } from 'react-native';
import {FontAwesome5} from '@expo/vector-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { StatusBar } from 'expo-status-bar';
import { faRobot, faPaperPlane } from '@fortawesome/free-solid-svg-icons';


export function Chat(){

    const [messages, setMessages] = useState([
        {
          id: 1,
          text: 'Olá! Eu sou uma inteligência artificial desenvolvida especialmente para auxiliar no acompanhamento farmacêutico. Minha função é garantir que você receba o melhor suporte possível no uso de medicamentos, com segurança e precisão.',
          sender: 'bot',
        },
      ]);

      const [input, setInput] = useState('');

        const handleSend = () => {
            if (!input.trim()) return;
            const userMessage = { id: Date.now(), text: input, sender: 'user' };
            setMessages((prevMessages) => [...prevMessages, userMessage]);
            setInput('');
          };

    return (

        <View style={styles.container}>
            <StatusBar style="dark" />

            <View style={styles.header}>
                <TouchableOpacity style={styles.backIcon}>
                    <FontAwesome5 name="arrow-left" size={20} color="#fff" />
                </TouchableOpacity>
                <Text style={styles.textoHeader}>Chat</Text>
                <TouchableOpacity style={styles.backIcon}>
                    <FontAwesome5 name="user-circle" size={20} color="#fff" />
                </TouchableOpacity>
            </View>

            
            <ScrollView style={styles.chatArea}>
            {messages.map((message) => (
                    <View
                    key={message.id}
                    style={[
                      styles.messageBubble,
                      message.sender === 'bot' ? styles.botMessage : styles.userMessage,
                    ]}
                  >
                    {message.sender === 'bot' && (
                    <View style={styles.botIcon}>
                        <FontAwesome5 icon="robot" size={24} color="#000" />
                    </View>
                    )}
                    <Text style={styles.messageText}>{message.text}</Text>
                </View>
                ))}
                        
            </ScrollView>

        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton} onPress={() =>
            setInput('Faça um breve resumo da bula')
          }>
            <Text style={styles.actionButtonText}>
              Faça um breve resumo da bula
            </Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton} onPress={() =>
            setInput('Com que frequência devo tomar o medicamento')
          }>
            <Text style={styles.actionButtonText}>
              Com que frequência devo tomar o medicamento
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            value={input}
            onChangeText={setInput}
            placeholder="Pergunte algo"
          />
          <TouchableOpacity onPress={handleSend} style={styles.sendButton}>
            <FontAwesome5 name="paper-plane" size={20} color="#fff" />
          </TouchableOpacity>
        </View>

        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    header: {
        marginTop: 32,
        height: 44,
        width: '100%',
        backgroundColor: '#000',
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    textoHeader: {
        color: '#fff',
        textAlign: 'center',
        justifyContent: 'center',
        lineHeight: 44,
        fontSize: 20,
    },
    backIcon: {
        width: 40, // Ensures consistent spacing for the back button
        justifyContent: 'center',
        alignItems: 'center',
    },
    chatArea: {
        flex: 1,
        backgroundColor: '#CBD5E1',
        paddingTop: 64,
        paddingHorizontal: 15,
    },
    messageBubble: {
        flexDirection: 'row',
        padding: 10,
        borderRadius: 10,
        marginBottom: 10,
        maxWidth: '80%',
    },
    userMessage: {
        alignSelf: 'flex-end',
        backgroundColor: '#007AFF',
    },
    botMessage: {
        alignSelf: 'flex-start',
        backgroundColor: '#fff',
        marginLeft: 43,
    },
    messageText: {
        color: '#000',
        fontSize: 16,
    },
    botIcon: {
        position: 'absolute',
        top: -0,
        left: -50,
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
    },
    actionButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingTop: 10,
        backgroundColor: '#CBD5E1',
    },
    actionButton: {
        flex: 1,
        backgroundColor: '#475569',
        paddingVertical: 10,
        borderRadius: 12,
        marginHorizontal: 5,
        alignItems: 'center',
    },
    actionButtonText: {
        color: '#fff',
        textAlign: 'center',
    },
    inputArea: {
        flexDirection: 'row',
        padding: 10,
        backgroundColor: '#CBD5E1',
    },
    textInput: {
      flex: 1,
      borderWidth: 1,
      borderColor: '#ddd',
      borderRadius: 20,
      paddingHorizontal: 15,
      backgroundColor: '#f1f1f1',
      marginRight: 10,
    },
    sendButton: {
        backgroundColor: '#475569',
        padding: 12,
        borderRadius: 20,
        justifyContent: 'center',
        alignItems: 'center',
    },
});

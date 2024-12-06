import React, {useState} from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from 'react-native';
import {FontAwesome5} from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';


export function Chat(){

    const [messages, setMessages] = useState([
        {
          id: 1,
          text: 'Olá! Eu sou uma inteligência artificial desenvolvida especialmente para auxiliar no acompanhamento farmacêutico. Minha função é garantir que você receba o melhor suporte possível no uso de medicamentos, com segurança e precisão.',
          sender: 'bot',
        },
      ]);

      const [inputText, setInputText] = useState('');
    
        const addMessage = (text: string, sender: string) => {
            setMessages([...messages, { id: messages.length + 1, text, sender }]);
        };
    
        const handleSend = () => {
            addMessage(inputText, 'user');
            setInputText('');
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
                <Text>Main</Text>
            </ScrollView>
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
    }
});

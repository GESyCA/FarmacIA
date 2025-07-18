import 'package:farmacia/app/data/models/user_model.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient _client;

  AuthService({required SupabaseClient client}) : _client = client;

  

  Future<AuthResponse> signIn(String email, String password) async {
    try {
      final response = await _client.auth.signInWithPassword(
        email: email,
        password: password,
      );

      if (response.user == null) {
        throw Exception("Usuário não encontrado.");
      }

      return response;
    } on AuthException catch (e) {
      throw Exception(e.message);
    } catch (e) {
      throw Exception("Erro inesperado ao tentar logar.");
    }
  }

  Future<AuthResponse> signUp(String email, String password) async {
    return await _client.auth.signUp(email: email, password: password);
  }

  Future<void> signUpWithDetails(UserModel user) async {
    final response = await _client.auth.signUp(
      email: user.email,
      password: user.senha,
      data: {
        'nome': user.nome,
        'telefone': user.telefone,
      },
    );

    if (response.user == null) {
      throw Exception('Failed to sign up: Invalid email or password.');
    }

    signOut();
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
  }

  Future<User?> getCurrentUser() async {
    final session = _client.auth.currentSession;
    return session?.user;
  }

  bool isAuthenticated() {
    return _client.auth.currentSession != null;
  }

  // listen to auth state changes
  Stream<AuthState> authStateChanges() {
    return _client.auth.onAuthStateChange;
  }

  Session? get currentSession {
    return _client.auth.currentSession;
  }
}

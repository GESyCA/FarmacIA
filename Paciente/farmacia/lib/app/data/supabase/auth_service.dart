import 'package:farmacia/app/data/models/user_model.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient _client = Supabase.instance.client;

  Future<AuthResponse> signIn(String email, String password) async {
    return await _client.auth.signInWithPassword(email: email, password: password);
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
}
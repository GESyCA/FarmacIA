import 'dart:convert';

import 'package:http/http.dart' as http;

abstract class IHttpClient {
  Future<http.Response> get(String endpoint);
  Future<http.Response> post(String endpoint, {required Map<String, dynamic> body});
  // post esperando um corpo que seja uma lista de mapas
  Future<http.Response> postList(String endpoint, {required List<Map<String, dynamic>> body});
}

class HttpClient implements IHttpClient {
  final String baseUrl;

  HttpClient({required this.baseUrl});

  @override
  Future<http.Response> get(String endpoint) async {
    final response = await http.get(Uri.parse('$baseUrl/$endpoint'));
    return response;
  }

  @override
  Future<http.Response> post(String endpoint, {required Map<String, dynamic> body}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/$endpoint'),
      headers: {
        'Content-Type': 'application/json',  // Setting the Content-Type header to JSON
        'Accept': 'application/json',         // Optional: Specify that you accept JSON responses
      },
      body: json.encode(body),
    );
    return response;
  }
  
  @override
  Future<http.Response> postList(String endpoint, {required List<Map<String, dynamic>> body}) {
    final response = http.post(
      Uri.parse('$baseUrl/$endpoint'),
      headers: {
        'Content-Type': 'application/json',  // Setting the Content-Type header to JSON
        'Accept': 'application/json',         // Optional: Specify that you accept JSON responses
      },
      body: json.encode(body),
    );
    return response;
  }
}
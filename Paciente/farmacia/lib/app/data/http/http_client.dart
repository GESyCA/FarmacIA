import 'package:http/http.dart' as http;

abstract class IHttpClient {
  Future<http.Response> get(String endpoint);
  Future<http.Response> post(String endpoint, {required Map<String, dynamic> body});
}

class HttpClient implements IHttpClient {
  final String baseUrl;

  HttpClient({required this.baseUrl});

  Future<http.Response> get(String endpoint) async {
    final response = await http.get(Uri.parse('$baseUrl/$endpoint'));
    return response;
  }

  Future<http.Response> post(String endpoint, {required Map<String, dynamic> body}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/$endpoint'),
      body: body,
    );
    return response;
  }
}
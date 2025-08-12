import 'package:farmacia/app/controllers/chat_controller.dart';
import 'package:farmacia/app/data/http/http_client.dart';
import 'package:farmacia/app/data/repositories/chat_repository.dart';
import 'package:get/get.dart';

class ChatBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ChatController>(
      () => ChatController(
        ChatRepository(
          httpClient: HttpClient(
            baseUrl: "https://farmaciajoasbarros123.serveo.net",
          ),
        ),
      ),
    );
  }
}

import 'package:farmacia/app/controllers/profile_controller.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class Statistics extends GetView<ProfileController> {

  Statistics({super.key});

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async {
        await controller.fetchMedicines();
      },
      backgroundColor: Colors.white,
      color: Color(0xFFB9160C),
      child: Container(
        width: MediaQuery.of(context).size.width,
        height: MediaQuery.of(context).size.height,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(24),
            topRight: Radius.circular(24),
          ),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          children: <Widget>[
            // header with tabs
            const SizedBox(
              height: 16,
            ),
            const Text(
              "INFORMAÇÕES",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(
              height: 20,
            ),
            Expanded(
              child: Obx(() => ListView.builder(
                              itemCount: controller.medicineNames.length,
                              itemBuilder: (context, index) {
                                final medicine = controller.medicineNames[index];
                                return Column(
                                  children: [
                                    Card(
                                      color: Colors.grey[100],
                                      child: ListTile(
                                        leading: const Icon(
                                          Icons.medication,
                                          color: Colors.red,
                                        ),
                                        title: Text(medicine.nome,
                                            style: const TextStyle(
                                              fontSize: 16,
                                              fontWeight: FontWeight.bold,
                                            )),
                                        trailing: IconButton(
                                          icon: const Icon(
                                            Icons.arrow_forward_ios,
                                            size: 16,
                                          ),
                                          onPressed: () {
                                            // A principio essa pagina seria pra exibir as estatisticas de acordo com a adesão do paciente ao medicamento
                                            // de acordo com os lembretes mas como essa funcionalidade não foi implementado ainda, iremos redirecionar para a pagina de edição do medicamento
                                            Get.toNamed(Routes.edit, arguments: medicine);
                                          },
                                        ),
                                      ),
                                    ),
                                    const SizedBox(
                                      height: 12,
                                    ),
                                  ],
                                );
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
      ),
    );
  }
}

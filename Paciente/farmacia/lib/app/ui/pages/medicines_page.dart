import 'package:farmacia/app/controllers/medicine_controller.dart';
import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:farmacia/app/ui/modal/full_space_dialog.dart';
import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:farmacia/app/ui/modal/delete_dialog.dart';
import 'package:get/get.dart';

class MedicinesPage extends GetView<MedicineController> {
  const MedicinesPage({super.key});

  void _showDeleteDialog(MedicineModel medicine, BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return DeleteDialog(
          medicine: medicine,
        );
      },
    );
  }

  void _showFullSpaceDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return FullSpaceDialog();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: 'Medicamentos'),
      body: Obx(
        () => controller.isLoading
            ? Center(
                child: CircularProgressIndicator(),
              )
            : RefreshIndicator(
                backgroundColor: Colors.white,
                color: Color(0xFFB9160C),
                onRefresh: () async {
                  controller.onInit();
                },
                child: Container(
                  width: MediaQuery.of(context).size.width,
                  height: MediaQuery.of(context).size.height,
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                  ),
                  child: Column(
                    children: [
                      SizedBox(
                        height: 16,
                      ),
                      _searchBar(context),
                      SizedBox(
                        height: 16,
                      ),
                      Flexible(
                        child: Container(
                          padding: EdgeInsets.zero,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            children: [
                              Padding(
                                padding: const EdgeInsets.only(
                                  top: 10,
                                  left: 20,
                                  right: 20,
                                  bottom: 2,
                                ),
                                child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    Text(
                                      "${controller.searchedItems.length} medicamentos",
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18,
                                      ),
                                    ),
                                    SizedBox(
                                      width: 50,
                                      height: 50,
                                      child: GetBuilder<MedicineController>(
                                      builder: (controller) => ElevatedButton(
                                        onPressed: () => controller.medicines.length < 6
                                          ? Get.toNamed(Routes.add_medicine)
                                          : _showFullSpaceDialog(context),
                                        style: ElevatedButton.styleFrom(
                                        shape: RoundedRectangleBorder(
                                          borderRadius:
                                            BorderRadius.circular(12),
                                        ),
                                        backgroundColor: Color(0xFFB9160C),
                                        padding: EdgeInsets.all(10),
                                        ),
                                        child: Icon(
                                        Icons.add,
                                        color: Colors.white,
                                        size: 30,
                                        ),
                                      ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Divider(
                                color: Colors.grey[300],
                                thickness: 1,
                              ),
                              Expanded(
                                child: ListView.builder(
                                  padding: EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 8,
                                  ),
                                  itemCount: controller.searchedItems.length,
                                  itemBuilder: (context, index) {
                                    final medicine =
                                        controller.searchedItems[index];
                                    return Card(
                                      color: Colors.white,
                                      child: ListTile(
                                        onTap: () {
                                          Get.toNamed(
                                            Routes.edit,
                                            arguments: medicine,
                                          );
                                        },
                                        contentPadding: EdgeInsets.symmetric(
                                          horizontal: 12,
                                        ),
                                        leading: GestureDetector(
                                          onTap: () {
                                            Get.toNamed(
                                              Routes.chat,
                                              arguments: medicine.nome,
                                            );
                                          },
                                          child: Container(
                                            width: 40,
                                            height: 40,
                                            decoration: BoxDecoration(
                                              color: Color(0xFFE8F3FF),
                                              borderRadius:
                                                  BorderRadius.circular(8),
                                            ),
                                            child: Center(
                                              child: Icon(
                                                Icons.chat_bubble_outline,
                                                color: Color(0xFF0A84FF),
                                                size: 24,
                                              ),
                                            ),
                                          ),
                                        ),
                                        title: Text(
                                          medicine.nome,
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        subtitle: Text(
                                            "Próximo: ${medicine.inicioTratamento.toLocal().toString().split(' ')[0]}"),
                                        trailing: IconButton(
                                          icon: const Icon(
                                            Icons.delete,
                                            color: Colors.red,
                                          ),
                                          onPressed: () {
                                            _showDeleteDialog(
                                                medicine, context);
                                          },
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
      ),
    );
  }

  TextField _searchBar(BuildContext context) {
    return TextField(
      controller: controller.searchController,
      onChanged: (value) {
        controller.filterSearchResults();
      },
      decoration: InputDecoration(
        hintText: "Buscar por medicamento",
        prefixIcon: GestureDetector(
          onTap: () {
            FocusScope.of(context).unfocus();
          },
          child: Icon(Icons.search),
        ),
        suffixIcon: Icon(Icons.mic),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1), width: 2),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
    );
  }
}

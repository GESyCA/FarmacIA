import 'package:farmacia/app/controllers/edit_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class EditPage extends GetView<EditController> {
  const EditPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: Text('Medicamento'),
      ),
      body: Column(
        children: [
          Text('Nome: ${controller.medicine.nome}'),
          Text('Dosagem: ${controller.medicine.forma}'),
        ],
      ),
    );
  }
}
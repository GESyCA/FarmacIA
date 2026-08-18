import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class DatabaseService {
  final SupabaseClient _client;

  DatabaseService({required SupabaseClient client}) : _client = client;

  final database = Supabase.instance.client.from("medicine");

  Future registerMedicine(MedicineModel medicine) async {
    return await database.insert(medicine.toJson()).select("id").single();
  }

  // list all medicines from the current user
  Future<List<MedicineModel>> getMedicines() async {
    final user = _client.auth.currentUser;
    final response = await database
        .select()
        .eq("user_id", user!.id)
        .order("created_at", ascending: false);

    return response.map((e) => MedicineModel.fromJson(e)).toList();
    }

    // update a medicine
    Future<void> updateMedicine(MedicineModel medicine) async {
      // imprimir o json do medicamento
      print(medicine.toJson());

      await database
          .update(medicine.toJson())
          .eq("id", medicine.id!)
          .maybeSingle();
    }

  // delete a medicine
  Future<void> deleteMedicine(MedicineModel medicine) async {
    await database.delete().eq("id", medicine.id!);
  }

  // retrieve the collumn 'nome' content for a especific user
  Future<List<String>> getMedicineNames() async {
    final user = _client.auth.currentUser;
    final response = await database
        .select("nome")
        .eq("user_id", user!.id)
        .order("created_at", ascending: false);

    return response.map((e) => e['nome'] as String).toList();
  }
}
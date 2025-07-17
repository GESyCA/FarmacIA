class MedicineModel {
  final int id;
  final String userId;
  final String nome;
  final bool receberNotificacao;
  final int? notificacoesPorDia;
  final String dose;
  final String forma;
  final DateTime inicioTratamento;
  final DateTime? fimTratamento;

  MedicineModel({
    required this.id,
    required this.userId,
    required this.nome,
    required this.receberNotificacao,
    this.notificacoesPorDia,
    required this.dose,
    required this.forma,
    required this.inicioTratamento,
    this.fimTratamento,
  });

  factory MedicineModel.fromJson(Map<String, dynamic> json) {
    return MedicineModel(
      id: json['id'] as int,
      userId: json['userId'] as String,
      nome: json['nome'] as String,
      receberNotificacao: json['receberNotificacao'] as bool,
      notificacoesPorDia: json['notificacoesPorDia'] as int?,
      dose: json['dose'] as String,
      forma: json['forma'] as String,
      inicioTratamento: DateTime.parse(json['inicioTratamento'] as String),
      fimTratamento: json['fimTratamento'] != null
          ? DateTime.parse(json['fimTratamento'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'nome': nome,
      'receber_notificacao': receberNotificacao,
      'notificacoes_por_dia': notificacoesPorDia,
      'dose': dose,
      'forma': forma,
      'inicio_tratamento': inicioTratamento.toIso8601String(),
      'fim_tratamento': fimTratamento?.toIso8601String(),
    };
  }
}

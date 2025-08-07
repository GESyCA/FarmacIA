class MedicineModel {
  final int? id;
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
      userId: json['user_id'] as String,
      nome: json['nome'] as String,
      receberNotificacao: json['receber_notificacao'] as bool,
      notificacoesPorDia: json['notificacoes_por_dia'] as int?,
      dose: json['dose'] as String,
      forma: json['forma'] as String,
      inicioTratamento: DateTime.parse(json['inicio_tratamento'] as String),
      fimTratamento: json['fim_tratamento'] != null
          ? DateTime.parse(json['fim_tratamento'] as String)
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

  // create tostring method for debugging
  @override
  String toString() {
    return 'MedicineModel{id: $id, userId: $userId, nome: $nome, receberNotificacao: $receberNotificacao, notificacoesPorDia: $notificacoesPorDia, dose: $dose, forma: $forma, inicioTratamento: $inicioTratamento, fimTratamento: $fimTratamento}';
  }

  MedicineModel copyWith({
    int? id,
    String? userId,
    String? nome,
    bool? receberNotificacao,
    int? notificacoesPorDia,
    String? dose,
    String? forma,
    DateTime? inicioTratamento,
    DateTime? fimTratamento,
  }) {
    return MedicineModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      nome: nome ?? this.nome,
      receberNotificacao: receberNotificacao ?? this.receberNotificacao,
      notificacoesPorDia: notificacoesPorDia,
      dose: dose ?? this.dose,
      forma: forma ?? this.forma,
      inicioTratamento: inicioTratamento ?? this.inicioTratamento,
      fimTratamento: fimTratamento,
    );
  }
}

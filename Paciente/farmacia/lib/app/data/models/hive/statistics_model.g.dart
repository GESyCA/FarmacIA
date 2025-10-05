// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'statistics_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class StatisticsModelAdapter extends TypeAdapter<StatisticsModel> {
  @override
  final int typeId = 2;

  @override
  StatisticsModel read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return StatisticsModel(
      scoreGeralPercentual: fields[1] as double,
      scoresDimensoesPercentual: (fields[2] as Map).cast<String, double>(),
    );
  }

  @override
  void write(BinaryWriter writer, StatisticsModel obj) {
    writer
      ..writeByte(2)
      ..writeByte(1)
      ..write(obj.scoreGeralPercentual)
      ..writeByte(2)
      ..write(obj.scoresDimensoesPercentual);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is StatisticsModelAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

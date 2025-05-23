import torch
import torch.nn as nn
import math

class SinusoidalEmbedding(nn.Module):
    def __init__(self, d_model, max_len=1000, scale=(0.001, 10000.0)):
        super().__init__()
        self.d_model = d_model
        self.scale_min, self.scale_max = scale
        self.max_len = max_len
        self.embeddings = self._build_embedding()
    def _build_embedding(self):
        pe = torch.zeros(self.max_len, self.d_model)
        position = torch.arange(0, self.max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, self.d_model, 2).float() * (-math.log(self.scale_max / self.scale_min) / self.d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)  # shape: (1, max_len, d_model)
    def forward(self, x):
        length = x.size(1)
        return self.embeddings[:, :length, :].to(x.device)

class PeakEncoder(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.intensity_proj = nn.Linear(1, d_model)
        self.mz_embed = SinusoidalEmbedding(d_model)

    def forward(self, mz, intensity):
        # mz, intensity: [B, N, 1]
        mz_embed = self.mz_embed(mz.squeeze(-1))  # [B, N, D]
        intensity_embed = self.intensity_proj(intensity)  # [B, N, D]
        return mz_embed + intensity_embed  # [B, N, D]

class PrecursorEncoder(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.mz_embed = SinusoidalEmbedding(d_model)
        self.charge_embed = nn.Embedding(11, d_model)  # charge 1-10

    def forward(self, precursor_mz, precursor_charge):
        # precursor_mz: [B, 1], precursor_charge: [B]
        mz_emb = self.mz_embed(precursor_mz)[:, 0, :]  # [B, D]
        charge_emb = self.charge_embed(precursor_charge)  # [B, D]
        return mz_emb + charge_emb  # [B, D]

class AminoAcidEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model, max_len=100):
        super().__init__()
        self.token_embed = nn.Embedding(vocab_size, d_model)
        self.pos_embed = SinusoidalEmbedding(d_model, max_len=max_len)

    def forward(self, seq):
        return self.token_embed(seq) + self.pos_embed(seq)

class CasanovoModel(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_layers=9, max_len=100):
        super().__init__()
        self.peak_encoder = PeakEncoder(d_model)
        self.precursor_encoder = PrecursorEncoder(d_model)
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead),
            num_layers=num_layers
        )
        self.aa_embedding = AminoAcidEmbedding(vocab_size, d_model, max_len)
        self.decoder = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(d_model=d_model, nhead=nhead),
            num_layers=num_layers
        )
        self.output_proj = nn.Linear(d_model, vocab_size)

def forward(self, mz, intensity, precursor_mz, precursor_charge, tgt_seq):
    # Encode MS2 peaks
    peak_embed = self.peak_encoder(mz, intensity)  # [B, N, D]
    precursor_embed = self.precursor_encoder(precursor_mz, precursor_charge).unsqueeze(1)  # [B, 1, D]
    encoder_input = torch.cat([peak_embed, precursor_embed], dim=1).permute(1, 0, 2)  # [N+1, B, D]
    memory = self.encoder(encoder_input)  # [N+1, B, D]

    tgt_embed = self.aa_embedding(tgt_seq).permute(1, 0, 2)  # [T, B, D]
    tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt_embed.size(0)).to(tgt_embed.device)
    decoded = self.decoder(tgt_embed, memory, tgt_mask=tgt_mask)  # [T, B, D]
    logits = self.output_proj(decoded).permute(1, 0, 2)  # [B, T, vocab]
    return logits



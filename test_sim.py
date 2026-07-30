import torch
import torchvision.transforms as transforms
import torchvision.models as models
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

m = models.mobilenet_v3_small(pretrained=True)
m.classifier = torch.nn.Identity()
m.eval()

t1 = torch.randn(1, 3, 224, 224)
t2 = t1 + torch.randn(1, 3, 224, 224) * 0.1 # slightly perturbed

v1 = m(t1).detach().numpy()
v2 = m(t2).detach().numpy()

print(cosine_similarity(v1, v2)[0][0])

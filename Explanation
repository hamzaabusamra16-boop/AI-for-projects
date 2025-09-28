1️⃣ مشروع تصنيف الأخبار العربية (NLP)
مقدمة
هذا المشروع يصنف الأخبار العربية إلى فئات متعددة باستخدام التعلم العميق (RNN + Embedding). يمكن إدخال نص والحصول على الفئة المتوقعة للأخبار.
البيانات
عدد الملفات: 4 ملفات CSV.
عدد الفئات: 20 فئة (مثل: Business, Sports, Tech…).
مصدر البيانات: ملفات محلية من dataset/dataset_for_projactOne/.
خطوات التحضير
دمج كل ملفات CSV في DataFrame واحد.
إزالة القيم المكررة.
تحويل النصوص لقوائم أرقام باستخدام Tokenizer و pad_sequences.
تحويل الفئات إلى تمثيل رقمي (One-Hot Encoding) باستخدام LabelEncoder و to_categorical.
النموذج
نوع النموذج: RNN (SimpleRNN).
الطبقات:
Embedding layer
SimpleRNN layer
Dense layers مع activation relu
طبقة خروج Dense مع activation softmax
loss function: categorical_crossentropy
optimizer: adam
epochs: 10
التدريب
تقسيم البيانات: 80% تدريب – 20% اختبار.
validation_split: 0.2 أثناء التدريب.
النتائج
دقة النموذج على البيانات التدريبية والاختبارية: متوسطة بسبب حجم البيانات الكبير.
ملاحظات: يمكن تحسين الدقة باستخدام LSTM أو Transformers لتقليل زمن التدريب وزيادة الأداء.
2️⃣ مشروع تصنيف صور الحيوانات (Computer Vision)
مقدمة
المشروع يصنف صور الحيوانات إلى أكثر من 90 فئة باستخدام CNN.
البيانات
مصدر البيانات: مجموعة صور dataset/archive-5/animals/animals/.
عدد الفئات: 90 فئة حيوانية مختلفة.
خطوات التحضير
استخدام ImageDataGenerator لتطبيع البيانات وعمل Augmentation.
تقسيم البيانات: 80% تدريب – 20% اختبار.
النموذج
نوع النموذج: CNN.
الطبقات:
Conv2D + MaxPooling2D
Conv2D + MaxPooling2D
Conv2D + MaxPooling2D
Flatten + Dense layers
طبقة خروج Dense مع activation softmax
loss function: categorical_crossentropy
optimizer: adam
epochs: 100
ملاحظات
النموذج قد يفشل إذا كانت الصور قليلة مقارنة بعدد الفئات.
يمكن استخدام Transfer Learning لتسريع التدريب وتحسين الدقة.
3️⃣ مشروع التنبؤ بأسعار المنازل (Machine Learning)
مقدمة
المشروع يستخدم ML تقليدي للتنبؤ بأسعار المنازل باستخدام مجموعة من المتغيرات الرقمية والفئوية.
البيانات
مصدر البيانات: dataset/realtor-data.zip.csv
preprocessing:
تحويل القيم الفئوية إلى أرقام باستخدام LabelEncoder.
التعامل مع القيم الفارغة: mean للأرقام، mode للفئات.
إزالة الأعمدة غير المهمة.
النموذج
استخدام عدة موديلات:
Linear Regression
Decision Tree
Random Forest
K-Neighbors
دمجها باستخدام VotingRegressor لتحسين الأداء.
التدريب
تقسيم البيانات: 80% تدريب – 20% اختبار.
مقياس الأداء: R² score على بيانات التدريب والاختبار.
ملاحظات
يمكن تحسين النتائج باستخدام Hyperparameter Tuning لكل نموذج.
يمكن تجربة Gradient Boosting أو XGBoost لتحقيق أداء أعلى.

import { Input, ValidationCmp } from '@/components';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { z } from 'zod';

const pdfSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  file: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, 'PDF file is required')
    .refine((files) => files[0]?.type === 'application/pdf', 'Only PDF files are allowed'),
});

type PdfFormData = z.infer<typeof pdfSchema>;

export default function NewPdf() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PdfFormData>({
    resolver: zodResolver(pdfSchema),
  });

  const onSubmit = (data: PdfFormData) => {
    console.log('PDF Upload:', data.title, data.file[0].name);
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
      <div className="card shadow p-4" style={{ width: '400px' }}>
        <h2 className="text-center mb-4">Upload PDF</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mb-3">
            <Input
              lable="Title"
              type="text"
              className={`form-control ${errors.title ? 'is-invalid' : ''}`}
              {...register('title')}
              autoComplete=""
            />

            {errors.title && <ValidationCmp message={errors.title?.message} />}
          </div>
          <div className="mb-3">
            <label htmlFor="file" className="form-label">
              PDF File
            </label>
            <input
              type="file"
              id="file"
              accept="application/pdf"
              className={`form-control ${errors.file ? 'is-invalid' : ''}`}
              {...register('file')}
            />
            {errors.file && (
              <div className="invalid-feedback">{errors.file.message?.toString()}</div>
            )}
          </div>
          <button type="submit" className="btn btn-primary w-100">
            Upload
          </button>
        </form>
        <p className="text-center mt-3">
          <Link to="/login">Back to Login</Link>
        </p>
      </div>
    </div>
  );
}
